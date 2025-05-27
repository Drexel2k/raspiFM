from __future__ import annotations

import time
from queue import Queue
from threading import Thread
import traceback

from common import socketstrings
from core.RaspiFMMessage import RaspiFMMessage
from core.players.Vlc import Vlc

class VlcRadioMonitor:
    __slots__ = ["__message_queue", "__vlcgetmeta_enabled"]
    __instance:VlcRadioMonitor = None
    __message_queue:Queue
    __vlcgetmeta_enabled:bool

    def __new__(cls, message_queue:Queue = None):
        if cls.__instance is None:
            if message_queue is None:
                raise ValueError("Missing argument on first call (initialization): message_queue")
            
            cls.__instance = super(VlcRadioMonitor, cls).__new__(cls)
            cls.__instance.__init(message_queue)
        return cls.__instance
    
    def __init(self, message_queue:Queue):
        self.__message_queue = message_queue
        self.__vlcgetmeta_enabled = False

    def start_meta_getter(self):
        self.__vlcgetmeta_enabled = True
        thread = Thread(target=self.__getmeta)
        thread.start()
    
    def __getmeta(self) -> None:
        try:
            #To debug remove comment on next line and in import statement for debugpy at beginning of file
            #debugpy.debug_this_thread()
            previous_meta = None

            #Split the sleep phase into 1 seconds that closing the app is more responsive e.g.
            #initla meta get after 2 seconds to get meta on start soon, afterwards meta is checked every 10 seconds.
            sleeptickslimit = 2
            sleeptickcount = 1
            while self.__vlcgetmeta_enabled:
                time.sleep(1)
                if sleeptickcount >= sleeptickslimit:
                    #First sleep phase is shorter than next spleep phases, so that first info is coming faster
                    if sleeptickslimit < 3:
                        sleeptickslimit = 10

                    sleeptickcount = 0

                    current_meta = Vlc().getmeta()
                    if current_meta != previous_meta:
                        previous_meta = current_meta
                        self.__message_queue.put(RaspiFMMessage({
                                                                    "message":"radio_change",
                                                                    "args":{
                                                                                "radio_currentplaying":current_meta}}))

                sleeptickcount += 1
        except:
            self.__vlcgetmeta_enabled = False
            self.__message_queue.put(RaspiFMMessage({
                                                        "message":socketstrings.shutdown_string,
                                                        "args":{
                                                                "reason":traceback.format_exc()
                                                                }
                                                        }))
    
    def stop_meta_getter(self) -> None:
        self.__vlcgetmeta_enabled = False