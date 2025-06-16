from __future__ import annotations

from PyQt6.QtCore import pyqtSignal, pyqtSlot, QObject

from common import socketstrings
from common.socket.raspifm_client.RaspiFMProxy import RaspiFMProxy
from touchui.QObjectSingletonMeta import QObjectSingletonMeta

#Proxy for the proxy, to enable the pyqtSignal to send messages to the ui proactively
#when the server sends messages without a prior request
class RaspiFMQtProxy(QObject, metaclass=QObjectSingletonMeta):
    __slots__ = []  

    core_notification_available = pyqtSignal(dict)

    def __init__(self):
        # Always call the parent class's __init__ first
        super().__init__()
        RaspiFMProxy(self.__core_notification_available)

    #callback method for the RaspiFMProxy which calls from another thread,
    #but signals and slots are thread safe
    @pyqtSlot(dict)
    def __core_notification_available(self, notification:dict):
        self.core_notification_available.emit(notification.message[socketstrings.message_string])
    
    def spotify_isplaying(self) -> bool:
        return RaspiFMProxy().spotify_isplaying()
    
    def radio_isplaying(self) -> bool:
        return RaspiFMProxy().radio_isplaying()
    
    def favorites_getlists(self) -> tuple:
        return RaspiFMProxy().favorites_getlists()
    
    def radio_play(self, station_uuid:str = None) -> None:
        RaspiFMProxy().radio_play(station_uuid)

    def radio_get_currentstation(self) -> dict:
        return RaspiFMProxy().radio_get_currentstation()
    
    def settings_touch_startwith(self) -> int:
        return RaspiFMProxy().settings_touch_startwith()
    
    def settings_touch_laststation(self) -> dict:
        return RaspiFMProxy().settings_touch_laststation()
    
    def stations_getstation(self, station_uuid:str) -> dict:
        return RaspiFMProxy().stations_getstation(station_uuid)
    
    def radio_getvolume(self) -> int:
        return RaspiFMProxy().radio_getvolume()
    
    def radio_set_currentstation(self, station_uuid:str) -> None:
        RaspiFMProxy().radio_set_currentstation(station_uuid)
    
    def settings_touch_runontouch(self) -> bool:
        return RaspiFMProxy().settings_touch_runontouch()
    
    def settings_all_loglevel(self) -> str:
        return RaspiFMProxy().settings_all_loglevel()
    
    def radio_getmeta(self) -> str:
        return RaspiFMProxy().radio_getmeta()

    def favorites_getdefaultlist(self) -> dict:
        return RaspiFMProxy().favorites_getdefaultlist()
    
    def favorites_get_any_station(self) -> dict:
        return RaspiFMProxy().favorites_get_any_station()
    
    def radio_stop(self) -> None:
        RaspiFMProxy().radio_stop()

    def radio_setvolume(self, volume:int) -> None:
        RaspiFMProxy().radio_setvolume(volume)

    def raspifm_getversion(self) -> str:
        return RaspiFMProxy().raspifm_getversion()
    
    def settings_set_touch_startwith (self, startwith:int) -> None:
        RaspiFMProxy().settings_set_touch_startwith(startwith)

    def spotify_currently_playing(self) -> dict:
        return RaspiFMProxy().spotify_currently_playing()
    
    def spotify_stop(self) -> None:
        RaspiFMProxy().spotify_stop()
    
    def players_status_subscribe(self) -> None:
        RaspiFMProxy().players_status_subscribe()

    def http_get_urlbinary_content_as_base64(self, url:str) -> str:
        return RaspiFMProxy().http_get_urlbinary_content_as_base64(url)
    
    def raspifm_shutdown(self) -> None:
        RaspiFMProxy().raspifm_shutdown()