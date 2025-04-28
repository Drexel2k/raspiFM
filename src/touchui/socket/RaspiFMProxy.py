from __future__ import annotations

from queue import Queue
from threading import Thread

from PyQt6.QtCore import pyqtSignal, pyqtSlot, QObject, QThreadPool

from common import strings
from touchui.CoreMonitor import CoreMonitor
from touchui.QObjectSingletonMeta import QObjectSingletonMeta
from touchui.socket.SocketManager import SocketManager

class RaspiFMProxy(QObject, metaclass=QObjectSingletonMeta):
    __slots__ = ["__socket_manager", "__thread_pool"]  

    __socket_manager:SocketManager
    __thread_pool:QThreadPool

    core_notification_available = pyqtSignal(dict)

    def __init__(self):

        # Always call the parent class's __init__ first
        super().__init__()
        self.__thread_pool = QThreadPool()
        read_queue = Queue()
        write_queue = Queue()
        self.__socket_manager = SocketManager(read_queue, write_queue)
        socket_read_thread = Thread(target=self.__socket_manager.read)
        socket_read_thread.start()
        socket_write_thread = Thread(target=self.__socket_manager.write)
        socket_write_thread.start()

        self.__socket_manager.core_notification_available.connect(self.__core_notification_available)
        core_monitor = CoreMonitor(self.__socket_manager)
        self.__thread_pool.start(core_monitor)

    @pyqtSlot(dict)
    def __core_notification_available(self, notification:dict):
        self.core_notification_available.emit(notification[strings.message_string])
    
    def spotify_isplaying(self) -> bool:
        result = self.__socket_manager.query_raspifm_core("spotify_isplaying", None, True)
        result = result[strings.result_string]
        return result
    
    def radio_isplaying(self) -> bool:
        result = self.__socket_manager.query_raspifm_core("radio_isplaying", None, True)
        result = result[strings.result_string]
        return result
    
    def favorites_getlists(self) -> tuple:
        result = self.__socket_manager.query_raspifm_core("favorites_getlists", None, True)
        result = result[strings.result_string]
        return result
    
    def radio_play(self, station_uuid:str = None) -> None:
        self.__socket_manager.query_raspifm_core("radio_play", {"station_uuid":station_uuid}, False)

    def radio_get_currentstation(self) -> dict:
        result = self.__socket_manager.query_raspifm_core("radio_get_currentstation", None, True)
        result = result[strings.result_string]
        return result
    
    def settings_touch_startwith(self) -> int:
        result = self.__socket_manager.query_raspifm_core("settings_touch_startwith", None, True)
        result = result[strings.result_string]
        return result
    
    def settings_touch_laststation(self) -> dict:
        result = self.__socket_manager.query_raspifm_core("settings_touch_laststation", None, True)
        result = result[strings.result_string]
        return result
    
    def stations_getstation(self, station_uuid:str) -> dict:
        result = self.__socket_manager.query_raspifm_core("stations_getstation", {"station_uuid":station_uuid}, True)
        result = result[strings.result_string]
        return result
    
    def radio_getvolume(self) -> int:
        result = self.__socket_manager.query_raspifm_core("radio_getvolume", None, True)
        result = result[strings.result_string]
        return result
    
    def radio_set_currentstation(self, station_uuid:str) -> None:
        self.__socket_manager.query_raspifm_core("radio_set_currentstation", {"station_uuid":station_uuid}, False)
    
    def settings_runontouch(self) -> bool:
        result = self.__socket_manager.query_raspifm_core("settings_runontouch", None, True)
        result = result[strings.result_string]
        return result
    
    def radio_getmeta(self) -> str:
        result = self.__socket_manager.query_raspifm_core("radio_getmeta", None, True)
        result = result[strings.result_string]
        return result
    
    def radio_send_stationclicked(self, station_uuid:str) -> None:
        self.__socket_manager.query_raspifm_core("radio_send_stationclicked", {"station_uuid":station_uuid}, False)

    def favorites_getdefaultlist(self) -> dict:
        result = self.__socket_manager.query_raspifm_core("favorites_getdefaultlist", None, True)
        result = result[strings.result_string]
        return result
    
    def favorites_get_any_station(self) -> dict:
        result = self.__socket_manager.query_raspifm_core("favorites_get_any_station", None, True)
        result = result[strings.result_string]
        return result
    
    def radio_stop(self) -> None:
        self.__socket_manager.query_raspifm_core("radio_stop", None, False)

    def radio_setvolume(self, volume:int) -> None:
        self.__socket_manager.query_raspifm_core("radio_setvolume", {"volume":volume}, False)

    def raspifm_getversion(self) -> str:
        result = self.__socket_manager.query_raspifm_core("raspifm_getversion", None, True)
        result = result[strings.result_string]
        return result
    
    def settings_set_touch_startwith (self, startwith:int) -> None:
        self.__socket_manager.query_raspifm_core("settings_set_touch_startwith", {"startwith":startwith}, False)

    def spotify_currentplaying(self) -> dict:
        result = self.__socket_manager.query_raspifm_core("spotify_currentplaying", None, True)
        result = result[strings.result_string]
        return result
    
    def spotify_stop(self) -> None:
        self.__socket_manager.query_raspifm_core("spotify_stop", None, False)
    
    def players_status_subscribe(self) -> None:
        self.__socket_manager.query_raspifm_core("players_status_subscribe", None, False)       

    def http_get_urlbinary_content_as_base64(self, url:str) -> str:
        result = self.__socket_manager.query_raspifm_core("http_get_urlbinary_content_asb64", {"url":url}, True)
        result = result[strings.result_string]
        return result
    
    def raspifm_shutdown(self) -> None:
        self.__socket_manager.close()