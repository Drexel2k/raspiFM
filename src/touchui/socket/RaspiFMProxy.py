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
        read_queue = Queue()
        write_queue = Queue()
        self.__socket_manager = SocketManager(read_queue, write_queue)
        socket_read_thread = Thread(target=self.__socket_manager.create_client_socket)
        socket_read_thread.start()

        socket_write_thread = Thread(target=self.__socket_manager.write)
        socket_write_thread.start()
    
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

    def radio_currentstation(self) -> dict:
        result = self.__socket_manager.query_raspifm_core("radio_currentstation", None, True)
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

    def http_get_urlbinary_content_as_base64(self, url:str) -> str:
        result = self.__socket_manager.query_raspifm_core("http_get_urlbinary_content_asb64", {"url":url}, True)
        result = result[strings.result_string]
        return result
    
    def raspifm_shutdown(self) -> None:
        self.__socket_manager.close()