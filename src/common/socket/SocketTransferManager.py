import struct
from socket import socket
from queue import Queue
from threading import Lock
import time

from common.socket.MessageResponse import MessageResponse
from common import json
from common import socketstrings

class SocketTransferManager:
    __slots__ = ["__socket", "__socket_address", "__read_queue", "__receive_buffer", "__current_message_header", "__current_message_header_length", "__requests_without_response", "__requests_without_response_lock", "__buffer_size", "__close_callback", "__socket_timeout"]
    __socket:socket
    __socket_address:str
    __read_queue:Queue
    __receive_buffer:bytes
    __requests_without_response_lock:Lock
    __requests_without_response:dict
    __buffer_size:int
    __close_callback:callable
    #todo: unify socket_timeouts which exist over several classes
    __socket_timeout:float

    #message can span over several read calls, bytes are removed, once a full part 
    #(header length, header or request content) is read, therefore read parts
    #are stored temporarily
    __current_message_header_length:int
    __current_message_header:dict

    def __init__(self, socket:socket, buffer_size:int, socket_address:str, request_queue:Queue, close_callback:callable=None, socket_timeout:float = 5):
        self.__socket = socket
        self.__socket_address = socket_address
        self.__read_queue = request_queue
        self.__receive_buffer = b""
        self.__requests_without_response_lock = Lock()
        self.__requests_without_response = {}
        self.__current_message_header_length = 0
        self.__current_message_header = None
        self.__buffer_size = buffer_size
        self.__close_callback = close_callback
        self.__socket_timeout = socket_timeout

    @property
    def socket(self) -> socket:
        return self.__socket
    
    @property
    def socket_address(self) -> str:
        return self.__socket_address

    #reader thread
    def read(self):
        try:
            data = self.__socket.recv(self.__buffer_size)
        except ConnectionResetError as conn_error:
            #connection reset by peer
            if conn_error.errno == 104:
                self.__close_callback(self)
            else:
                raise conn_error

        if len(data) > 1:
            self.__receive_buffer += data
            self.__process_receive_buffer()
        else:
            if not self.__close_callback is None:
                self.__close_callback(self)

    #reader thread    
    def __process_receive_buffer(self):
        if not self.__current_message_header_length > 0:
            self.__process_header_length()

        if self.__current_message_header_length >0:
            if self.__current_message_header is None:
                self.__process_header()

        if not self.__current_message_header is None:
            self.__process_message()

    #reader thread  
    def __process_header_length(self):
        header_length = 2
        if len(self.__receive_buffer) >= header_length:
            self.__current_message_header_length = struct.unpack(">H", self.__receive_buffer[:header_length])[0] #>H big-endian unsigned short
            self.__receive_buffer = self.__receive_buffer[header_length:]

    #reader thread
    def __process_header(self):
        if len(self.__receive_buffer) >= self.__current_message_header_length:
            self.__current_message_header = json.deserialize_from_string_or_bytes(self.__receive_buffer[:self.__current_message_header_length], socketstrings.utf8_string)
            self.__receive_buffer = self.__receive_buffer[self.__current_message_header_length:]
            for requestheader in (
                socketstrings.contentencoding_string,
                socketstrings.contentlength_string
            ):
                if requestheader not in self.__current_message_header:
                    raise ValueError(f"Missing required header '{requestheader}'.")
                
            if socketstrings.messageid_string not in self.__current_message_header and socketstrings.responseto_string not in self.__current_message_header:
                raise ValueError(f"Missing required header 'messageid' or 'responseto'.")

    #reader thread
    def __process_message(self):
        message_length = self.__current_message_header[socketstrings.contentlength_string]
        if not len(self.__receive_buffer) >= message_length:
            return

        header = self.__current_message_header

        message = None
        if message_length > 0:
            data = self.__receive_buffer[:message_length]
            self.__receive_buffer = self.__receive_buffer[message_length:]        
            message = json.deserialize_from_string_or_bytes(data, socketstrings.utf8_string)
        
        self.__current_message_header_length = 0
        self.__current_message_header = None
        
        message_response = None
        if socketstrings.messageid_string in header:
            message_response = MessageResponse(self.__socket_address, 
                                                    {
                                                        socketstrings.header_string: header
                                                    })
            
            if not message is None:
               message_response.message[socketstrings.message_string] = message  
        else:
            with self.__requests_without_response_lock:
                message_response = self.__requests_without_response.pop(header[socketstrings.responseto_string])
                message_response.response = {
                                                socketstrings.header_string: header
                                            }
                
                if not message is None:
                    message_response.response[socketstrings.response_string] = message  
                
                message_response.response_ready.set()
                
        self.__read_queue.put(message_response)
        self.__process_receive_buffer()

    #writer thread
    #messages must be JSON serializable, only Python basics types allowed
    def send(self, message_response:MessageResponse, additional_header:dict):
        content_bytes = b""
        header = {}
        if message_response.response is None and message_response.response_exception is None:
            content_bytes = json.serialize_to_string_or_bytes(message_response.message[socketstrings.message_string], socketstrings.utf8_string)

            if message_response.is_query:
                with self.__requests_without_response_lock:
                    self.__requests_without_response[additional_header[socketstrings.messageid_string]] = message_response
        else:
            if message_response.response_exception is None:
                content_bytes = json.serialize_to_string_or_bytes(message_response.response, socketstrings.utf8_string)
            else:
                #On caught exception no response is there, but we need a respoonse which just sends a header
                message_response.response = {}
                
            header[socketstrings.responseto_string] = message_response.message[socketstrings.header_string][socketstrings.messageid_string]
            
        header[socketstrings.contentencoding_string] = socketstrings.utf8_string,
        header[socketstrings.contentlength_string] = len(content_bytes)
        
        header.update(additional_header)

        if message_response.response is None and message_response.response_exception is None:
            message_response.message[socketstrings.header_string] = header
        else:
            message_response.response[socketstrings.header_string] = header
            
        header_bytes = json.serialize_to_string_or_bytes(header, socketstrings.utf8_string)
        message_header = struct.pack(">H", len(header_bytes))
        message_bytes = message_header + header_bytes + content_bytes

        sent = 0
        current_package = 0
        previous_package = 0
        sleep_counter = 0
        sleep_counter_limit = self.__socket_timeout * 10
        try:
            while len(message_bytes) > 0:
                buff = message_bytes[:self.__buffer_size]
                try:
                    sent = self.__socket.send(buff)

                    message_bytes= message_bytes[sent:]
                    previous_package = current_package
                    current_package = current_package + 1
                #if socket buffer is full, BlockingIOError occurs, we have to wait a bit until the client has read data
                except BlockingIOError as BlockingIOError_exception:
                    if previous_package == current_package:
                        sleep_counter = sleep_counter + 1
                    else:
                        sleep_counter = 0

                    if sleep_counter > sleep_counter_limit:
                        raise BlockingIOError_exception

                    print("Waiting for Uinux socket...")
                    time.sleep(0.1)
        except Exception as transfer_exception:
            #if sending fails also no response can be expected, so therefore set sending and response,
            #transfer_exception must be checked after waiting for either of message_send or response_ready
            #calls waiting for response can also continue if sending failed
            message_response.transfer_exception = transfer_exception
            message_response.response_ready.set()
        finally:
            message_response.message_sent.set()
            

    #reader thread
    def close(self):
        self.__socket.close()
        self.__socket = None