from __future__ import annotations

from datetime import datetime
from datetime import timedelta
import logging
from pathlib import Path
from uuid import UUID
from os import path

from core.LogLevel import LogLevel
from core.StartWith import StartWith
from core.business.InvalidOperationError import InvalidOperationError
from core.json.JsonSerializer import JsonSerializer
from core.json.JsonDeserializer import JsonDeserializer
from core.Settings import Settings, UserSettings
from core.http.radiobrowserapi import requestbase
from core.http.radiobrowserapi import stationapi
from core.http.radiobrowserapi.data.RadioStationApi import RadioStationApi
from core.http.radiobrowserapi import listapi
from core.http.basics import httpcontent
from core.business.Direction import Direction
from core.business.CountryList import CountryList
from core.business.LanguageList import LanguageList
from core.business.TagList import TagList
from core.business.Favorites import Favorites
from core.business.RadioStations import RadioStations
from core.business.RadioStation import RadioStation
from core.business.FavoriteList import FavoriteList
from core.players.DBusSpotifyMonitor import DBusSpotifyMonitor
from core.players.VlcRadioMonitor import VlcRadioMonitor
from core.players.Spotify import Spotify
from core.players.SpotifyInfo import SpotifyInfo
from core.players.Vlc import Vlc
from common import log, utils

#todo: maybe split public core interface in several proxy classes
class RaspiFM:
    __slots__ = ["__favorites", "__radiostations", "__settings", "__version"]
    __instance:RaspiFM = None
    __radiostations:RadioStations
    __favorites:Favorites
    __settings:Settings
    __version:str

    @property
    def version(self) -> str:
        return self.__version
    
    def __new__(cls, spotify_info:SpotifyInfo = None):
        if cls.__instance is None:
            cls.__instance = super(RaspiFM, cls).__new__(cls)
            cls.__instance.__init(spotify_info)
        return cls.__instance
    
    def __init(self, spotify_info:SpotifyInfo):
        self.__version = "1.1.0"
        requestbase.version = self.__version

        self.__settings = Settings()

        if not Path(self.__settings.serialization_directory).is_dir():
            Path(self.__settings.serialization_directory).mkdir(parents=True, exist_ok=True)

        if not Path(self.__settings.serialization_directory, "cache/").is_dir():    
            Path(self.__settings.serialization_directory, "cache/").mkdir(parents=True, exist_ok=True)
            
        JsonSerializer(self.__settings.serialization_directory)
        JsonDeserializer(self.__settings.serialization_directory)

        self.__radiostations = JsonDeserializer().get_radiostations()
        if self.__radiostations is None:
            self.__radiostations = RadioStations.from_default()

        self.__favorites = JsonDeserializer().get_favorites(self.__radiostations)
        if self.__favorites is None:
            self.__favorites = Favorites.from_default()

        usersettings = JsonDeserializer().get_usersettings()
        self.__settings.usersettings = usersettings if usersettings else UserSettings.from_default()

        log_level = self.__settings.usersettings.all_loglevel.value
        logger = logging.getLogger(log.core_logger_name)
        if log_level < 100:
            log_level = log_level * 10

            logger.setLevel(log_level)
        else:
            logger.disabled = True

        Vlc().volume = self.__settings.usersettings.touch_volume

        Spotify().currentlyplaying = spotify_info
    
    def stationapis_get(self, name:str, country:str, language:str, tags:list, orderby:str, reverse:bool, page:int) -> list:
        stations_api = stationapi.query_stations_advanced(name, country, language, tags, orderby, reverse, page)
        return list(map(lambda radiostationdict: RadioStationApi(radiostationdict), stations_api))
    
    def stations_getstation(self, station_uuid:UUID) -> RadioStation:
        return self.__radiostations.get_station(station_uuid)
    
    def stations_delete_station_if_not_used(self, uuid:UUID, serialize:bool=True) -> None:
        station = self.stations_getstation(uuid)

        deletestation = True
        for favlist in self.__favorites.favoritelists:
            stationresult = next((stationinternal for stationinternal in favlist.stations if stationinternal.radiostation == station), None)
            if not stationresult is None:
                deletestation = False
                break
        
        if uuid == self.__settings.usersettings.touch_laststation:
            deletestation = False

        if deletestation:
            self.__radiostations.remove_station(station)
            if serialize:
                JsonSerializer().serialize_radiostations(self.__radiostations)
    
    def countries_get(self) -> CountryList:
        countrylist = JsonDeserializer().get_countrylist()

        sevendays = timedelta(days=7)
        if countrylist is None or countrylist.lastupdate + sevendays < datetime.now():
            countrylistapi = listapi.query_countrylist()
            countrylist = CountryList.from_default({ countryinternal["name"] : countryinternal["iso_3166_1"] for countryinternal in countrylistapi })
            JsonSerializer().serialize_countrylist(countrylist)

        return countrylist
    
    def languages_get(self) -> LanguageList:
        languagelist = JsonDeserializer().get_languagelist()

        sevendays = timedelta(days=7)
        if languagelist is None or languagelist.lastupdate + sevendays < datetime.now():
            languagelistapi = listapi.query_languagelist()  
            languagelist = LanguageList.from_default({ languageinternal["name"] : languageinternal["iso_639"] for languageinternal in languagelistapi })
            JsonSerializer().serialize_languagelist(languagelist)

        return languagelist
    
    def tags_get(self, filter:str=None) -> TagList:
        taglist = JsonDeserializer().get_taglist()

        sevendays = timedelta(days=7)
        if taglist is None or taglist.lastupdate + sevendays < datetime.now():
            taglistapi = listapi.query_taglist()  
            taglist = TagList.from_default([ taginternal["name"] for taginternal in taglistapi ])
            JsonSerializer().serialize_taglist(taglist)

        if not filter is None:
            taglist.filter(filter)
            
        return taglist
    
    def favorites_add_stationtolist(self, station_uuid:UUID, favlist_uuid:UUID) -> None:
        station = self.__radiostations.get_station(station_uuid)

        if station is None:
            radiostationapi = stationapi.query_station(station_uuid)
            station = RadioStation.from_default(radiostationapi.stationuuid,
                                   radiostationapi.name,
                                   radiostationapi.url_resolved,
                                   radiostationapi.codec,                                   
                                   radiostationapi.countrycode,
                                   radiostationapi.languagecodes,
                                   radiostationapi.homepage,
                                   None if utils.str_isnullorwhitespace(radiostationapi.favicon) else httpcontent.get_urlbinary_content_as_base64(radiostationapi.favicon),
                                   None if utils.str_isnullorwhitespace(radiostationapi.favicon) else path.splitext(radiostationapi.favicon)[1][1:],
                                   radiostationapi.bitrate,
                                   list(radiostationapi.tags))

        self.__favorites.get_list(favlist_uuid).add_station(station)
        self.__radiostations.add_station(station)

        JsonSerializer().serialize_radiostations(self.__radiostations)
        JsonSerializer().serialize_favorites(self.__favorites)

    def favorites_remove_stationfromlist(self, station_uuid:UUID, favlist_uuid:UUID) -> None:
        station = self.__radiostations.get_station(station_uuid)

        self.__favorites.get_list(favlist_uuid).remove_station(station)
        JsonSerializer().serialize_favorites(self.__favorites)

        self.stations_delete_station_if_not_used(station.uuid)
    
    def favorites_getlists(self) -> tuple:
        return self.__favorites.favoritelists
    
    def favorites_addlist(self) -> FavoriteList:
        favoritelist = self.__favorites.add_favoritelist()
        JsonSerializer().serialize_favorites(self.__favorites)
        return favoritelist
    
    def favorites_deletelist(self, favlist_uuid:UUID) -> None:
        favlist = self.__favorites.get_list(favlist_uuid)
        station_uuids = []
        if not favlist is None:
            for stationentry in favlist.stations:
                station_uuids.append(stationentry.radiostation.uuid)

        self.__favorites.delete_favoritelist(favlist_uuid)
        JsonSerializer().serialize_favorites(self.__favorites)

        for station_uuid in station_uuids:
            self.stations_delete_station_if_not_used(station_uuid, False)

        JsonSerializer().serialize_radiostations(self.__radiostations)

    def favorites_getdefaultlist(self) -> FavoriteList:
        return self.__favorites.get_default()
    
    def favorites_getlist(self, favlist_uuid:UUID) -> FavoriteList:
        return self.__favorites.get_list(favlist_uuid)

    def favorites_get_any_station(self) -> RadioStation:
        return self.__favorites.get_any_station()
    
    def favorites_changelistproperty(self, favlist_uuid:UUID, property:str, value:str) -> None:
        if property == "isdefault":
            self.__favorites.change_default(favlist_uuid, True if value.strip().lower() == "true" else False)
        elif property == "name":
            changelist = self.__favorites.get_list(favlist_uuid)
            changelist.name = value
        else: 
            raise TypeError(f"Change of property \"{property}\" supported.")
        
        JsonSerializer().serialize_favorites(self.__favorites)

    def favorites_movelist(self, favlist_uuid:UUID, direction:str) -> None:
        direction = Direction[direction]
        self.__favorites.move_list(favlist_uuid, direction)
        
        JsonSerializer().serialize_favorites(self.__favorites)

    def favorites_move_station_in_list(self, favlist_uuid:UUID, station_uuid:UUID, direction:str) -> None:
        direction = Direction[direction]
        self.__favorites.move_station_in_list(favlist_uuid, station_uuid, direction)
        
        JsonSerializer().serialize_favorites(self.__favorites)

    def settings_touch_runontouch(self) -> bool:
        return self.__settings.usersettings.touch_runontouch
    
    def settings_web_defaultlanguage(self) -> str:
        return self.__settings.usersettings.web_defaultlanguage
    
    def settings_web_defaultcountry(self) -> str:
        return self.__settings.usersettings.web_defaultcountry
    
    def settings_touch_startwith(self) -> StartWith:
        return self.__settings.usersettings.touch_startwith
    
    def settings_set_touch_startwith(self, startwith:StartWith) -> None:
        self.__settings.usersettings.touch_startwith = startwith
        JsonSerializer().serialize_usersettings(self.__settings.usersettings)

    def settings_touch_laststation(self) -> UUID:
        return self.__settings.usersettings.touch_laststation
    
    def settings_all_loglevel(self) -> LogLevel:
        return self.__settings.usersettings.all_loglevel
    
    def settings_changeproperty(self, property:str, value:str) -> None:
        if property == "country":
            countrylist = self.countries_get()

            if value in countrylist.countrylist.values() or value == "nofilter":
                self.__settings.usersettings.web_defaultcountry = value
        elif property == "lang":
            languagelist = self.languages_get()

            if value in languagelist.languagelist or value == "nofilter":
                self.__settings.usersettings.web_defaultlanguage = value
        else: 
            raise InvalidOperationError(104, f"Change of property \"{property}\" supported.")
        
        JsonSerializer().serialize_usersettings(self.__settings.usersettings)

    def radio_play(self, station_uuid:UUID = None) -> None:
        station = self.__radiostations.get_station(station_uuid)
        Vlc().play(station)
        VlcRadioMonitor().start_meta_getter()
        
        if not station is None:
            original_laststation = self.__settings.usersettings.touch_laststation
            self.__settings.usersettings.touch_laststation = station.uuid

            if not original_laststation is None:
                self.stations_delete_station_if_not_used(original_laststation)

            JsonSerializer().serialize_usersettings(self.__settings.usersettings)
        else:
            station = Vlc().currentstation

        if RaspiFM().settings_touch_runontouch(): #otherwise we are on dev most propably so we don't send a click on every play
            stationapi.send_stationclicked(station.uuid)

    def radio_stop(self) -> None:
        VlcRadioMonitor().stop_meta_getter()
        Vlc().stop()

    def radio_isplaying(self) -> bool:
        return Vlc().isplaying
    
    def radio_get_currentstation(self) -> RadioStation:
        return Vlc().currentstation

    def radio_set_currentstation(self, station_uuid:UUID) -> None:
        station = self.__radiostations.get_station(station_uuid)
        Vlc().currentstation = station

        original_laststation = self.__settings.usersettings.touch_laststation
        self.__settings.usersettings.touch_laststation = station.uuid

        if not original_laststation is None:
            self.stations_delete_station_if_not_used(original_laststation)

        JsonSerializer().serialize_usersettings(self.__settings.usersettings)

    def radio_setvolume(self, volume:int) -> None:
        Vlc().volume = volume
        self.__settings.usersettings.touch_volume = volume
        JsonSerializer().serialize_usersettings(self.__settings.usersettings)

    def radio_getvolume(self) -> int:
        return Vlc().volume

    def radio_getmeta(self) -> str:
        return Vlc().getmeta()

    def radio_send_stationclicked(self, station_uuid:UUID) -> None:
        stationapi.send_stationclicked(station_uuid)

    def spotify_change(self, spotify_info:SpotifyInfo) -> None:
        if not spotify_info is None:
            Vlc().stop()

        Spotify().currentlyplaying = spotify_info

    def spotify_isplaying(self) -> bool:
        return Spotify().isplaying

    def spotify_currently_playing(self) -> SpotifyInfo:
        return Spotify().currentlyplaying
    
    def spotify_stop(self) -> None:
        DBusSpotifyMonitor().stop_spotify()

    def raspifm_getversion(self) -> str:
        return self.version
    
    def http_get_urlbinary_content_asb64(self, url:str) ->str:
        return httpcontent.get_urlbinary_content_as_base64(url)

    def raspifm_shutdown(self) -> None:
        Vlc().shutdown()