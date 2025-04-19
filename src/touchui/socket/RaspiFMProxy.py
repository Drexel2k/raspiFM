from __future__ import annotations

from queue import Queue
from threading import Thread

from common import strings
from touchui.socket.SocketManager import SocketManager

class RaspiFMProxy:
    __slots__ = ["__socket_manager"]
    __instance:RaspiFMProxy = None
    __socket_manager:SocketManager

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(RaspiFMProxy, cls).__new__(cls)
            cls.__instance.__init()
        return cls.__instance
    
    def __init(self):
        request_queue = Queue()
        write_queue = Queue()
        self.__socket_manager = SocketManager(request_queue, write_queue)
        socket_read_thread = Thread(target=self.__socket_manager.create_client_socket)
        socket_read_thread.start()

        socket_write_thread = Thread(target=self.__socket_manager.write)
        socket_write_thread.start()
    
    def spotify_isplaying(self) -> bool:
        result = self.__socket_manager.query_raspifm_core("spotify_isplaying", None, True)
        result = result[strings.result_string]
        return result
