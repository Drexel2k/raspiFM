import selectors
import socket as modsocket
from socket import socket
from selectors import DefaultSelector
from queue import Queue
from threading import Thread

from common.socket.SocketTransferManager import SocketTransferManager
from common import strings
from common.socket.MessageResponse import MessageResponse
from threading import Event

class SocketManager:
    #No multi threading in selector mechanisms!
    __slots__ = ["__socket_selector", "__read_queue", "__write_queue", "__socket_transfermanager", "__messageid"]
    __socket_selector:DefaultSelector
    __read_queue:Queue
    __write_queue:Queue
    __socket_transfermanager:SocketTransferManager
    __messageid:int

    def __init__(self, request_queue:Queue, response_queue:Queue):
        self.__socket_selector = DefaultSelector()
        self.__read_queue = request_queue
        self.__write_queue = response_queue
        self.__messageid = 0

        socket_read_thread = Thread(target=self.__monitor_read_queue)
        socket_read_thread.start()

    #reader thread
    def create_client_socket(self):
        client_socket = socket(modsocket.AF_UNIX, modsocket.SOCK_STREAM)
        client_socket.setblocking(False)
        client_socket.connect(strings.socketpath_string)
        self.__socket_transfermanager = SocketTransferManager(client_socket, strings.socketpath_string, self.__read_queue)
        self.__socket_selector.register(client_socket, selectors.EVENT_READ, data=self.__socket_transfermanager)

        while True:
            events = self.__socket_selector.select(timeout=None)
            for event in events:
                socket_transfermanager = event[0].data
                socket_transfermanager.read()

    #writer thread
    def write(self):
        while True:
            write = self.__write_queue.get()
            self.__socket_transfermanager.send(write)

    #monitor thread
    def __monitor_read_queue(self):
        while True:
            message_response = self.__read_queue.get()
            #messages with response are handled by reponse ready event/
            #query_raspifm_core
            if message_response.response is None:
                #send message/event to main window
                pass

    #main thread
    def query_raspifm_core(self, query:str, args:list, is_query:bool) -> dict:
        request_dict =  { 
                            strings.header_string:{strings.messageid_string:self.__get_messageid()}, 
                            strings.message_string:{ strings.message_string: query, "args":args}
                        } 
        request = MessageResponse(strings.socketpath_string, request_dict, is_query)
        self.__write_queue.put(request)
        if is_query:
            request.response_ready.wait()
            return request.response[strings.response_string]
        
        return

    def __get_messageid(self) -> int:
        self.__messageid = self.__messageid + 1
        return self.__messageid