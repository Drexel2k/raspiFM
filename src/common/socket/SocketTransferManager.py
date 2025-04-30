import struct
from socket import socket
from queue import Queue
from threading import Lock

from common.socket.MessageResponse import MessageResponse
from common import json
from common import strings

class SocketTransferManager:
    __slots__ = ["__socket", "__socket_address", "__read_queue", "__receive_buffer", "__current_message_header", "__current_message_header_length", "__requests_without_response", "__requests_without_response_lock", "__buffer_size", "__close_callback"]
    __socket:socket
    __socket_address:str
    __read_queue:Queue
    __receive_buffer:bytes
    __requests_without_response_lock:Lock
    __requests_without_response:dict
    __buffer_size:int
    __close_callback:int

    #message can span over several read calls, bytes are removed, once a full part 
    #(header length, header or request content) is read, therefore read parts
    #are stored temporarily
    __current_message_header_length:int
    __current_message_header:dict

    def __init__(self, socket:socket, buffer_size:int, socket_address:str, request_queue:Queue, close_callback=None):
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
            self.__current_message_header = json.deserialize_from_string_or_bytes(self.__receive_buffer[:self.__current_message_header_length], strings.utf8_string)
            self.__receive_buffer = self.__receive_buffer[self.__current_message_header_length:]
            for requestheader in (
                strings.contentencoding_string,
                strings.contentlength_string
            ):
                if requestheader not in self.__current_message_header:
                    raise ValueError(f"Missing required header '{requestheader}'.")
                
            if strings.messageid_string not in self.__current_message_header and strings.responseto_string not in self.__current_message_header:
                raise ValueError(f"Missing required header 'messageid' or 'responseto'.")

    #reader thread
    def __process_message(self):
        message_length = self.__current_message_header[strings.contentlength_string]
        if not len(self.__receive_buffer) >= message_length:
            return
        data = self.__receive_buffer[:message_length]
        self.__receive_buffer = self.__receive_buffer[message_length:]
        header = self.__current_message_header
        message = json.deserialize_from_string_or_bytes(data, strings.utf8_string)
        
        self.__current_message_header_length = 0
        self.__current_message_header = None
        
        message_response = None
        if strings.messageid_string in header:
            message_response = MessageResponse(self.__socket_address, 
                                                    {
                                                        strings.header_string: header,
                                                        strings.message_string: message
                                                    })
        else:
            with self.__requests_without_response_lock:
                message_response = self.__requests_without_response.pop(header[strings.responseto_string])
                message_response.response = {
                                                strings.header_string: header,
                                                strings.response_string: message
                                            }
                
                message_response.response_ready.set()
                
        self.__read_queue.put(message_response)
        self.__process_receive_buffer()

    #writer thread
    #messages must die JSON serializable, only Python basics types allowed
    def send(self, message_response:MessageResponse):
        content_bytes = b""
        header = {} 
        if message_response.response is None:
            content_bytes = json.serialize_to_string_or_bytes(message_response.message[strings.message_string], strings.utf8_string)
            header = {
                        strings.messageid_string:message_response.message[strings.header_string][strings.messageid_string],
                        strings.contentencoding_string: strings.utf8_string,
                        strings.contentlength_string: len(content_bytes),
                    }

            message_response.message[strings.header_string] = header 

            if message_response.is_query:
                with self.__requests_without_response_lock:
                    self.__requests_without_response[message_response.message[strings.header_string][strings.messageid_string]] = message_response
        else:
            content_bytes = json.serialize_to_string_or_bytes(message_response.response, strings.utf8_string)
            header = {
                        strings.responseto_string:message_response.message[strings.header_string][strings.messageid_string],
                        strings.contentencoding_string: strings.utf8_string,
                        strings.contentlength_string: len(content_bytes),
                    }
            
            message_response.response[strings.header_string] = header
            
        header_bytes = json.serialize_to_string_or_bytes(header, strings.utf8_string)
        message_header = struct.pack(">H", len(header_bytes))
        message_bytes = message_header + header_bytes + content_bytes

        sent = 0
        try:
            while len(message_bytes) > 0:
                buff = message_bytes[:self.__buffer_size]
                sent = self.__socket.send(buff)
                message_bytes= message_bytes[sent:]
            
            message_response.message_sent.set()
        except Exception as transfer_exception:
            message_response.transfer_exception = transfer_exception
            if message_response.is_query:
                message_response.response_ready.set()

    #reader thread
    def close(self):
        self.__socket.close()
        self.__socket = None