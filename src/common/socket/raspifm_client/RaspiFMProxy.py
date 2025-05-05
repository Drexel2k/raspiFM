from __future__ import annotations

from queue import Queue
from threading import Thread
from uuid import UUID

from common import strings
from common.socket.raspifm_client.SocketManager import SocketManager

class RaspiFMProxy():
    __slots__ = ["__socket_manager", "__read_queue", "__read_queue_callback", "__socket_read_thread", "__socket_write_thread"]
    __instance:RaspiFMProxy = None

    __socket_read_thread:Thread
    __socket_write_thread:Thread

    __read_queue:Queue
    __socket_manager:SocketManager
    __read_queue_callback:callable

    def __new__(cls, read_queue_callback:callable = None):
        if cls.__instance is None:
            #instance initialization may fail, if raspifm service is not available.
            #therefore set instance only once we have a working instance
            instance_internal =  super(RaspiFMProxy, cls).__new__(cls)
            instance_internal.__init(read_queue_callback)
            if not instance_internal is None:
                cls.__instance = instance_internal
        return cls.__instance
    
    def __init(self, read_queue_callback:callable):
        self.__read_queue = Queue()
        write_queue = Queue()
        self.__socket_manager = SocketManager(self.__read_queue, write_queue)
        self.__socket_read_thread = Thread(target=self.__socket_manager.read)
        self.__socket_read_thread.start()
        self.__socket_write_thread = Thread(target=self.__socket_manager.write)
        self.__socket_write_thread.start()

        self.__read_queue_callback = read_queue_callback
        read_queue_thread = Thread(target=self.__monitor_read_queue)
        read_queue_thread.start()

    #monitor thread
    def __monitor_read_queue(self) -> None:
        run = True
        while True and run:
            queue_item = self.__read_queue.get()
            if isinstance(queue_item, str):
                #Python 3.12 doesn't support Queue.shutdown yet()
                if queue_item == "shutdown":
                    run=False
                    continue

            #messages with response are handled by response ready event/
            #query_raspifm_core
            if queue_item.response is None and not self.__read_queue_callback is None:
                self.__read_queue_callback(queue_item)
    
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

    def spotify_currently_playing(self) -> dict:
        result = self.__socket_manager.query_raspifm_core("spotify_currently_playing", None, True)
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

    def countries_get(self) -> dict:
        result = self.__socket_manager.query_raspifm_core("countries_get", None, True)
        result = result[strings.result_string]
        return result

    def languages_get(self) -> dict:
        result = self.__socket_manager.query_raspifm_core("languages_get", None, True)
        result = result[strings.result_string]
        return result
    
    def settings_web_defaultcountry(self) -> str:
        result = self.__socket_manager.query_raspifm_core("settings_web_defaultcountry", None, True)
        result = result[strings.result_string]
        return result
    
    def settings_web_defaultlanguage(self) -> str:
        result = self.__socket_manager.query_raspifm_core("settings_web_defaultlanguage", None, True)
        result = result[strings.result_string]
        return result
    
    def favorites_getlist(self, favlist_uuid:str) -> dict:
        result = self.__socket_manager.query_raspifm_core("favorites_getlist", {"favlist_uuid":favlist_uuid}, True)
        result = result[strings.result_string]
        return result

    def stationapis_get(self, name:str, country:str, language:str, tags:list, orderby:str, reverse:bool, page:int) -> list:
        result = self.__socket_manager.query_raspifm_core("stationapis_get", {
                                                                                "name":name,
                                                                                "country":country,
                                                                                "language":language,
                                                                                "tags":tags,
                                                                                "orderby":orderby,
                                                                                "reverse":reverse,
                                                                                "page":page},
                                                                                True)
        result = result[strings.result_string]
        return result
    
    def tags_get(self, filter:str=None):
        result = self.__socket_manager.query_raspifm_core("tags_get", {"filter":filter}, True)
        result = result[strings.result_string]
        return result
    
    def favorites_add_stationtolist(self, station_uuid:str, favlist_uuid:str) -> None:
        self.__socket_manager.query_raspifm_core("favorites_add_stationtolist", {"station_uuid":station_uuid, "favlist_uuid":favlist_uuid}, False)

    def favorites_remove_stationfromlist(self, station_uuid:str, favlist_uuid:str) -> None:
        self.__socket_manager.query_raspifm_core("favorites_remove_stationfromlist", {"station_uuid":station_uuid, "favlist_uuid":favlist_uuid}, False)

    def favorites_addlist(self) -> dict:
        result = self.__socket_manager.query_raspifm_core("favorites_addlist", None, True)
        result = result[strings.result_string]
        return result
    
    def favorites_changelistproperty(self, favlist_uuid:str, property:str, value:str) -> None:
        self.__socket_manager.query_raspifm_core("favorites_changelistproperty", {"favlist_uuid":favlist_uuid, "property":property, "value":value}, False)

    def favorites_deletelist(self, favlist_uuid:str) -> None:
        self.__socket_manager.query_raspifm_core("favorites_deletelist", {"favlist_uuid":favlist_uuid}, False)

    def favorites_movelist(self, favlist_uuid:str, direction:str) -> None:
        self.__socket_manager.query_raspifm_core("favorites_movelist", {"favlist_uuid":favlist_uuid, "direction":direction}, False)

    def favorites_move_station_in_list(self, favlist_uuid:str, station_uuid:str, direction:str) -> None:
        self.__socket_manager.query_raspifm_core("favorites_move_station_in_list", {"favlist_uuid":favlist_uuid, "station_uuid":station_uuid, "direction":direction}, False)
        
    def settings_changeproperty(self, property:str, value:str) -> None:
        self.__socket_manager.query_raspifm_core("settings_changeproperty", {"property":property, "value":value}, False)

    def raspifm_shutdown(self) -> None:
        self.__socket_manager.query_raspifm_core("raspifm_shutdown", None, False)
        self.__socket_manager.shutdown()
        self.__read_queue.put("shutdown")