import os
import selectors
import socket as modsocket
from socket import socket
from selectors import DefaultSelector
from queue import Queue

from common.socket.SocketTransferManager import SocketTransferManager
from common import strings

class SocketManager:
    #No multi threading in selector mechanisms!
    __slots__ = ["__socket_selector", "__read_queue", "__write_queue", "__client_sockets"]
    __socket_selector:DefaultSelector
    __read_queue:Queue
    __write_queue:Queue
    __client_sockets:dict

    def __init__(self, read_queue:Queue, response_queue:Queue):
        self.__socket_selector = DefaultSelector()
        self.__read_queue = read_queue
        self.__write_queue = response_queue
        self.__client_sockets = {}

    #reader thread 
    def __create_client_socket(self, client_socket_param):
        client_socket, _ = client_socket_param.accept()
        #we work with unix sockets, so we don't have an address here,
        #so we take the file descriptor
        socket_address = str(client_socket.fileno())
        client_socket.setblocking(False)
        socket_transfermanager = SocketTransferManager(client_socket, socket_address, self.__read_queue)
        self.__client_sockets[socket_address] = socket_transfermanager
        self.__socket_selector.register(client_socket, selectors.EVENT_READ, socket_transfermanager)

    #reader thread
    def create_server_socket(self):
        raspifm_socket = socket(modsocket.AF_UNIX, modsocket.SOCK_STREAM)
        if os.path.exists(strings.socketpath_string):
            os.remove(strings.socketpath_string)

        raspifm_socket.bind(strings.socketpath_string)
        raspifm_socket.listen()
        raspifm_socket.setblocking(False)
        self.__socket_selector.register(raspifm_socket, selectors.EVENT_READ, None)

        while True:
            events = self.__socket_selector.select(timeout=None)
            for event in events:
                if event[0].data is None:
                    self.__create_client_socket(event[0].fileobj)
                else:
                    socket_transfermanager = event[0].data
                    socket_transfermanager.read()

    #writer thread
    def write(self):
        while True:
            write = self.__write_queue.get()
            self.__client_sockets[write.socket_address].send(write) 