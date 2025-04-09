import selectors
import struct

from common import json
from common import utils

class SocketTransferManager:
    __slots__ = ["__selector", "__sock", "__recv_buffer", "__send_buffer", "__jsonheader", "__request", "__response_created"]

    def __init__(self, selector, sock):
        self.__selector = selector
        self.__sock = sock
        self.__recv_buffer = b""
        self.__send_buffer = b""
        self.__jsonheader_length = None
        self.__jsonheader = None
        self.__request = None
        self.__response_created = False

    def process_events(self, mask:int):
        if mask & selectors.EVENT_READ:
            self.__read()
        if mask & selectors.EVENT_WRITE:
            self.__write()

    def __read(self):
        data = self.__sock.recv(4096)

        if data:
            self.__recv_buffer += data
        else:
            raise RuntimeError("Peer closed.")

        if self.__jsonheader_length is None:
            self.__process_jsonheader_length()

        if self.__jsonheader_length is not None:
            if self.__jsonheader is None:
                self.__process_jsonheader()

        if self.__jsonheader is not None:
            if self.__request is None:
                self.__process_request()

    def __write(self):
        if self.__request:
            if not self.__response_created:
                self.__create_response()

        self.__write()
        
    def __process_jsonheader_length(self):
        jsonheader_length = 2
        if len(self.__recv_buffer) >= jsonheader_length:
            self.__jsonheader_length = struct.unpack(">H", self.__recv_buffer[:jsonheader_length])[0] #>H big-endian unsigned short
            self.__recv_buffer = self.__recv_buffer[jsonheader_length:]

    def __process_jsonheader(self):
        if len(self.__recv_buffer) >= self.__jsonheader_length:
            self.__jsonheader = json.deserialize_from_string_or_bytes(self.__recv_buffer[:self.__jsonheader_length], utils.utf8_string)
            self.__recv_buffer = self.__recv_buffer[self.__jsonheader_length:]
            for requestheader in (
                "messageid",
                "content-length"
            ):
                if requestheader not in self.__jsonheader:
                    raise ValueError(f"Missing required header '{requestheader}'.")

    def __process_request(self):
        content_length = self.__jsonheader["content-length"]
        if not len(self.__recv_buffer) >= content_length:
            return
        data = self.__recv_buffer[:content_length]
        self.__recv_buffer = self.__recv_buffer[content_length:]
        self.__request = json.deserialize_from_string_or_bytes(data, utils.utf8_string)

        #Set selector to listen for write events, we'read one request we want to answer first.
        #No multithreading in select mechanisms!
        #Another message from the client may also be in queue or partially received, we care about
        #that after answering the current message
        self.__selector.modify(self.__sock, selectors.EVENT_WRITE, data=self)
    
    def __create_response(self):
        query = self.__request.get("query")
        if query.strip().lower() == "bye":
            self.__close()
            #answer = "blub based on action and param"
            #content = {"result": answer}
        else:
            content = {"result": f"Error: invalid query '{query}'."}
        
        message = self.__create_message(content)
        self.__response_created = True
        self.__send_buffer += message
    
    def __create_message(self, content_bytes:bytes):
        jsonheader = {"content-length": len(content_bytes)}
        jsonheader_bytes = json.serialize_to_string_or_bytes(jsonheader, utils.utf8_string)
        return struct.pack(">H", len(jsonheader_bytes)) + jsonheader_bytes + content_bytes
    
    def __write(self):
        if self.__send_buffer is not None:
            sent = self.__sock.send(self.__send_buffer)
            self.__send_buffer = self.__send_buffer[sent:]
            # Continue reading after sending, no multi threading!
            if len(self.__send_buffer) <= 0:
                self.__selector.modify(self.__sock, selectors.EVENT_READ, data=self)

    def __close(self):
        self.__selector.unregister(self.__sock)
        self.__sock.close()
        self.__sock = None