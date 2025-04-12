import os
import selectors
import socket as modsocket
from socket import socket
from selectors import DefaultSelector
from queue import Queue

from core.socket.SocketTransferManager import SocketTransferManager

class SocketManager:
    #No multi threading in selector mechanisms!
    __slots__ = ["__socket_selector", "__request_queue", "__response_queue", "__client_sockets"]
    __socket_selector:DefaultSelector
    __request_queue:Queue
    __response_queue:Queue
    __client_sockets:dict

    def __init__(self, request_queue:Queue, response_queue:Queue):
        self.__socket_selector = DefaultSelector()
        self.__request_queue = request_queue
        self.__response_queue = response_queue

    #reader thread 
    def __create_client_socket(self, sock):
        socket, socket_address = sock.accept()
        socket.setblocking(False)
        socket_transfermanager = SocketTransferManager(self.__socket_selector, socket, socket_address, self.__request_queue)
        self.__client_sockets[socket_address] = socket_transfermanager
        self.__socket_selector.register(socket, selectors.EVENT_READ, socket_transfermanager)

    #reader thread
    def create_server_socket(self):
        socketpath = "/tmp/raspifm_socket"
        raspifm_socket = socket(modsocket.AF_UNIX, modsocket.SOCK_STREAM)
        if os.path.exists(socketpath):
            os.remove(socketpath)

        raspifm_socket.bind(socketpath)
        raspifm_socket.listen()
        raspifm_socket.setblocking(False)
        self.__socket_selector.register(raspifm_socket, selectors.EVENT_READ, None)

        while True:
            events = self.__socket_selector.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    self.__create_client_socket(key.fileobj)
                else:
                    socket_transfermanager = key.data
                    socket_transfermanager.read()

    #writer thread
    def send_responses(self):
        while True:
            response = self.__response_queue.get()
            self.__client_sockets[response.socket_address].send_response(response) 