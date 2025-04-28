from __future__ import annotations

from datetime import time
from queue import Queue
from threading import Thread

from core.RaspiFMMessage import RaspiFMMessage
from core.players.Vlc import Vlc

class VlcRadioMonitor:
    __slots__ = ["__message_queue", "__spotify_dbusname", "__dbus_spotify_filter", "__dbus_connection", "__dbus_queue", "__dbus_proxy"]
    __instance:VlcRadioMonitor = None
    __message_queue:Queue

    def __new__(cls, message_queue:Queue = None):
        if cls.__instance is None:
            if message_queue is None:
                raise ValueError("Missing argument on first call (initialization): message_queue")
            
            cls.__instance = super(VlcRadioMonitor, cls).__new__(cls)
            cls.__instance.__init(message_queue)
        return cls.__instance
    
    def __init(self, message_queue:Queue):
        self.__message_queue = message_queue

    def start_meta_getter(self):
        self.__vlcgetmeta_enabled = True
        server_socket_read_thread = Thread(target=self.__getmeta)
        server_socket_read_thread.start()
    
    def __getmeta(self) -> None:
        #To debug remove comment on next line and in import statement for debugpy at beginning of file
        #debugpy.debug_this_thread()
        previous_meta= "-1"

        #Split the sleep phase into 0.5 seconds that closing the app is more responsive e.g.
        sleeptickslimit = 4
        sleeptickcount = 1
        while self.__vlcgetmeta_enabled:
            time.sleep(0.5)
            if sleeptickcount >= sleeptickslimit:
                #First sleep phase is shorter than next spleep phases, so that first info is coming faster
                if sleeptickslimit < 5:
                    sleeptickslimit = 20

                sleeptickcount = 0

                current_meta = Vlc().getmeta()
                if current_meta != previous_meta:
                    previous_meta = current_meta
                    self.__message_queue.put(RaspiFMMessage({
                                                                "message":"vlc_change",
                                                                "args":{
                                                                            "vlc_nowplaying_metadata":current_meta}}))

            sleeptickcount += 1
    
    def stop_meta_getter(self) -> None:
        self.__vlcgetmeta_enabled = False