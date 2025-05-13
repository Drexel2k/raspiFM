import os
import selectors
import socket as modsocket
from socket import socket
from selectors import DefaultSelector
from queue import Queue
from threading import Lock

from common.socket.MessageResponse import MessageResponse
from common.socket.SocketTransferManager import SocketTransferManager
from common import strings

class SocketManager:
    #No multi threading in selector mechanisms!
    __slots__ = ["__socket_selector", "__read_queue", "__write_queue", "__client_sockets", "__socket_closed_callback", "__messageid", "__run_selector", "__sockets_lock"]
    __socket_selector:DefaultSelector
    __read_queue:Queue
    __write_queue:Queue
    __client_sockets:dict
    __socket_closed_callback:callable
    __messageid:int
    __run_selector:bool
    __sockets_lock:Lock

    def __init__(self, read_queue:Queue, response_queue:Queue, socket_closed_callback:callable=None):
        self.__socket_selector = DefaultSelector()
        self.__run_selector = True
        self.__read_queue = read_queue
        self.__write_queue = response_queue
        self.__client_sockets = {}
        self.__socket_closed_callback = socket_closed_callback
        self.__messageid = 0
        self.__sockets_lock = Lock()

        raspifm_socket = socket(modsocket.AF_UNIX, modsocket.SOCK_STREAM)
        if os.path.exists(strings.core_socketpath_string):
            os.remove(strings.core_socketpath_string)

        raspifm_socket.bind(strings.core_socketpath_string)
        raspifm_socket.listen()
        raspifm_socket.setblocking(False)
        self.__socket_selector.register(raspifm_socket, selectors.EVENT_READ, None)
        
    #reader thread 
    def __create_client_socket(self, client_socket_param):
        client_socket, _ = client_socket_param.accept()
        #we work with unix sockets, so we don't have an address here,
        #so we take the file descriptor
        socket_address = str(client_socket.fileno())
        client_socket.setblocking(False)

        with self.__sockets_lock:
            socket_transfermanager = SocketTransferManager(client_socket, 4096, socket_address, self.__read_queue, self.__close_client_socket)
            self.__client_sockets[socket_address] = socket_transfermanager
            self.__socket_selector.register(client_socket, selectors.EVENT_READ, socket_transfermanager)

    def read(self) -> None:
        while self.__run_selector:
            #No other possibility to get the selector out of the block, even TemporaryFile doesn't work
            events = self.__socket_selector.select(1)
            for event in events:
                if event[0].data is None:
                    self.__create_client_socket(event[0].fileobj)
                else:
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

            self.__client_sockets[queue_item.socket_address].send(queue_item)

    #main thread
    def send_message_to_client(self, client_socket_address:str, query:str, args:dict) -> None:
        request_dict =  { 
                            strings.header_string:{strings.messageid_string:self.__get_messageid()}, 
                            strings.message_string:{ strings.message_string: query, strings.args_string:args}
                        } 
        request = MessageResponse(client_socket_address, request_dict)
        self.__write_queue.put(request)
        request.message_sent.wait()
        if not request.transfer_exception is None:
            raise request.transfer_exception

    def __get_messageid(self) -> int:
        self.__messageid = self.__messageid + 1
        return self.__messageid

    def __close_client_socket(self, socket_transfermanager:SocketTransferManager) -> None:
        with self.__sockets_lock:
            self.__socket_selector.unregister(socket_transfermanager.socket)
            self.__client_sockets[socket_transfermanager.socket_address].close()
            del self.__client_sockets[socket_transfermanager.socket_address]
            if not self.__socket_closed_callback is None:
                self.__socket_closed_callback(socket_transfermanager.socket_address)

    def shutdown(self) -> None:
        self.__run_selector = False
        self.__write_queue.put("shutdown")

        self.__run_selector = False
        
        with self.__sockets_lock:
            for _, socket_transfer_manager in self.__client_sockets.items():
                self.__socket_selector.unregister(socket_transfer_manager.socket)
                socket_transfer_manager.socket.close()

            self.__socket_selector.close()