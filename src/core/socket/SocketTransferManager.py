import struct
from socket import socket
from queue import Queue

from core.socket.RequestResponse import RequestResponse
from common import json
from common import utils


class SocketTransferManager:
    __slots__ = ["__socket", "__socket_address", "__request_queue", "__receive_buffer", "__current_request_header", "__current_request_header_length"]
    __socket:socket
    __socket_address:str
    __request_queue:Queue
    __receive_buffer:bytes
    
    #message can span over several read calls, bytes are removed, once a full part 
    #(header length, header or request content) is read, therefore read parts
    #are stored temporarily
    __current_request_header_length:int
    __current_request_header:dict

    def __init__(self, socket, socket_address, request_queue):
        self.__socket = socket
        self.__socket_address = socket_address
        self.__request_queue = request_queue
        self.__receive_buffer = b""

    #reader thread
    def read(self):
        data = self.__sock.recv(4096)

        if data:
            self.__receive_buffer += data
        else:
            raise RuntimeError("Peer closed.")
        
        self.__process_receive_buffer()

    #reader thread    
    def __process_receive_buffer(self):
        if not self.__current_request_header_length > 0:
            self.__process_header_length()

        if self.__current_request_header_length >0:
            if self.__current_request_header is None:
                self.__process_header()

        if self.__current_request_header is not None:
            self.__process_request()

    #reader thread  
    def __process_header_length(self):
        header_length = 2
        if len(self.__receive_buffer) >= header_length:
            self.__current_request_header_length = struct.unpack(">H", self.__receive_buffer[:header_length])[0] #>H big-endian unsigned short
            self.__receive_buffer = self.__receive_buffer[header_length:]

    #reader thread
    def __process_header(self):
        if len(self.__receive_buffer) >= self.__current_request_header_length:
            self.__current_request_header = json.deserialize_from_string_or_bytes(self.__receive_buffer[:self.__current_request_header_length], utils.utf8_string)
            self.__receive_buffer = self.__receive_buffer[self.__current_request_header_length:]
            for requestheader in (
                "messageid",
                "content-encoding",
                "content-length"
            ):
                if requestheader not in self.__current_request_header:
                    raise ValueError(f"Missing required header '{requestheader}'.")

    #reader thread
    def __process_request(self):
        request_length = self.__current_request_header["content-length"]
        if not len(self.__receive_buffer) >= request_length:
            return
        data = self.__receive_buffer[:request_length]
        self.__receive_buffer = self.__receive_buffer[request_length:]
        header = self.__current_request_header
        request = json.deserialize_from_string_or_bytes(data, utils.utf8_string)
        if request["query"].strip().lower() == "bye":
            self.__close()
            return
        
        self.__current_request_header_length = 0
        self.__current_request_header = None
        
        self.__request_queue.put(RequestResponse(self.__socket_address, 
                                                {
                                                    "header": header,
                                                    "request": request
                                                    }))
        
        self.__process_receive_buffer()

    #writer thread
    def send_response(self, request_response:RequestResponse):
        response_bytes = json.deserialize_from_string_or_bytes(request_response.response, utils.utf8_string)
        header = {
                    "responseto:":request_response.request.header.messageid,
                    "content-encoding": utils.utf8_string,
                    "content-length": len(response_bytes),
                }
        header_bytes = self._json_encode(header, utils.utf8_string)
        message_header = struct.pack(">H", len(header_bytes))
        message_bytes = message_header + header_bytes + response_bytes

        sent = 0
        while len(message_bytes) > 0:
            sent = self.__socket.send(message_bytes)
            message_bytes= message_bytes[sent:]

    #reader thread
    def __close(self):
        self.__selector.unregister(self.__sock)
        self.__sock.close()
        self.__socket = None