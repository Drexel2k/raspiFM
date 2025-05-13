import selectors
import socket as modsocket
from socket import socket
from selectors import DefaultSelector
from queue import Queue

from common.socket.SocketTransferManager import SocketTransferManager
from common import strings
from common.socket.MessageResponse import MessageResponse

class SocketManager():
    #No multi threading in selector mechanisms!
    __slots__ = ["__socket_selector", "__write_queue", "__socket_transfermanager", "__messageid", "__run_selector"]
    __socket_selector:DefaultSelector

    __write_queue:Queue
    __socket_transfermanager:SocketTransferManager
    __messageid:int
    __run_selector:bool

    def __init__(self, read_queue:Queue, response_queue:Queue):
        super().__init__()
        self.__socket_selector = DefaultSelector()
        self.__run_selector = True
        self.__write_queue = response_queue
        self.__messageid = 0
        
        client_socket = socket(modsocket.AF_UNIX, modsocket.SOCK_STREAM)
        client_socket.setblocking(False)
        client_socket.connect(strings.core_socketpath_string)
        self.__socket_transfermanager = SocketTransferManager(client_socket, 4096, strings.core_socketpath_string, read_queue)
        self.__socket_selector.register(client_socket, selectors.EVENT_READ, data=self.__socket_transfermanager)

    #reader thread
    def read(self) -> None:
        while self.__run_selector:
            #No other possibility to get the selector out of the block, even TemporaryFile doesn't work
            events = self.__socket_selector.select(1)
            for event in events:
                socket_transfermanager = event[0].data
                socket_transfermanager.read()

    #writer thread
    def write(self) -> None:
        run = True
        while run:
            queue_item = self.__write_queue.get()
            if isinstance(queue_item, str):
                #Python 3.12 doesn't support Queue.shutdown yet()
                if queue_item == "shutdown":
                    run=False
                    continue

            self.__socket_transfermanager.send(queue_item)

    #main thread
    def query_raspifm_core(self, query:str, args:dict, is_query:bool) -> dict:
        request_dict =  { 
                            strings.header_string:{strings.messageid_string:self.__get_messageid()}, 
                            strings.message_string:{ strings.message_string: query, strings.args_string:args}
                        } 
        request = MessageResponse(strings.core_socketpath_string, request_dict, is_query)
        self.__write_queue.put(request)
        if is_query:
            request.response_ready.wait()

            if not request.transfer_exception is None:
                raise request.transfer_exception
            
            return request.response[strings.response_string]
        else:
            request.message_sent.wait()
            if not request.transfer_exception is None:
                raise request.transfer_exception

    def __get_messageid(self) -> int:
        self.__messageid = self.__messageid + 1
        return self.__messageid
    
    def shutdown(self) -> None:
        self.__write_queue.put("shutdown")
        self.__run_selector = False

        self.__socket_selector.unregister(self.__socket_transfermanager.socket)
        self.__socket_transfermanager.socket.close()

        self.__run_selector = False
        self.__socket_selector.close()