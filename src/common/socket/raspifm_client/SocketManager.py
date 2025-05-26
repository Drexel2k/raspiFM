import selectors
import socket as modsocket
from socket import socket
from selectors import DefaultSelector
from queue import Queue

from common.socket.SocketTransferManager import SocketTransferManager
from common import socketstrings
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
        client_socket.connect(socketstrings.core_socketpath_string)
        self.__socket_transfermanager = SocketTransferManager(client_socket, 4096, socketstrings.core_socketpath_string, read_queue)
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
                if queue_item == socketstrings.shutdown_string:
                    run=False
                    continue

            self.__socket_transfermanager.send(queue_item, {socketstrings.messageid_string:self.__get_messageid()})

    #main thread
    def query_raspifm_core(self, query:str, args:dict, is_query:bool) -> dict:       
        request = MessageResponse(socketstrings.core_socketpath_string, {
            socketstrings.message_string: {socketstrings.message_string: query, socketstrings.args_string:args}
        }, True)
        self.__write_queue.put(request)

        request.response_ready.wait()

        if not request.transfer_exception is None:
            raise request.transfer_exception
        
        request.response_ready.wait()        
        if request.response[socketstrings.header_string][socketstrings.service_status_string][socketstrings.code_string] != 200:
            raise ValueError(f'Something went wrong in raspiFM core. Status code: {request.response[socketstrings.header_string][socketstrings.service_status_string][socketstrings.code_string]}, status message: {request.response[socketstrings.header_string][socketstrings.service_status_string][socketstrings.message_string]}, status additional info code: {request.service_status[socketstrings.additional_info_code_string]}, status additional info message: {request.service_status[socketstrings.additional_info_message_string]}.')
        
        if is_query:
            return request.response[socketstrings.response_string]

    def __get_messageid(self) -> int:
        self.__messageid = self.__messageid + 1
        return self.__messageid
    
    def shutdown(self) -> None:
        self.__write_queue.put(socketstrings.shutdown_string)
        self.__run_selector = False

        self.__socket_selector.unregister(self.__socket_transfermanager.socket)
        self.__socket_transfermanager.socket.close()

        self.__run_selector = False
        self.__socket_selector.close()