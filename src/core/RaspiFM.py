from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from pathlib import Path
from uuid import UUID
from os import path

from .json.JsonSerializer import JsonSerializer
from .json.JsonDeserializer import JsonDeserializer
from .Settings import Settings
from .http.radiobrowserapi import stationapi
from .http.radiobrowserapi.data.RadioStationApi import RadioStationApi
from .http.radiobrowserapi import listapi
from .http.basics import httpcontent
from .business.CountryList import CountryList
from .business.LanguageList import LanguageList
from .business.TagList import TagList
from .business.Favorites import Favorites
from .business.RadioStations import RadioStations
from .business.RadioStation import RadioStation
from .business.FavoriteList import FavoriteList
from ..utils import utils

class RaspiFM:
    __slots__ = ["__favorites_obj", "__radiostations_obj", "__settings"]
    __instance:RaspiFM = None
    __radiostations_obj:RadioStations
    __favorites_obj:Favorites
    __settings:Settings

    @property
    def __radiostations(self) -> RadioStations:
        if(not self.__radiostations_obj):
            stations = JsonDeserializer().get_radiostations()
            if(not stations):
                stations = RadioStations()
            self.__radiostations_obj = stations

        return self.__radiostations_obj
    
    @property
    def __favorites(self) -> Favorites:
        if(not self.__favorites_obj):
            favorites = JsonDeserializer().get_favorites(self.__radiostations)
            if(not favorites):
                favorites = Favorites()
            self.__favorites_obj = favorites

        return self.__favorites_obj
    
    @property
    def settings(self) -> Settings:
        return self.__settings
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(RaspiFM, cls).__new__(cls)
            cls.__instance.__init()
        return cls.__instance
    
    def __init(self):
        self.__settings = Settings()

        if not Path(self.__settings.serialization_directory).is_dir():
            Path(self.__settings.serialization_directory).mkdir(parents=True, exist_ok=True)

        if not Path(self.__settings.serialization_directory, "cache/").is_dir():    
            Path(self.__settings.serialization_directory, "cache/").mkdir(parents=True, exist_ok=True)
            
        JsonSerializer(self.__settings.serialization_directory)
        JsonDeserializer(self.__settings.serialization_directory)
        self.__radiostations_obj = None
        self.__favorites_obj = None

        usersettings = JsonDeserializer().get_usersettings()
        if(usersettings):
            self.__settings.usersettings = usersettings        
    
    def stations_get(self, name:str, country:str, language:str, tags:list, orderby:str, reverse:bool, page:int) -> list:
        return list(map(lambda radiostationdict: RadioStationApi(radiostationdict),
                   stationapi.query_stations_advanced(name, country, language, tags, orderby, reverse, page)))
    
    def countries_get(self) -> CountryList:
        countrylist = JsonDeserializer().get_countrylist()

        sevendays = timedelta(days=7)
        if (not countrylist or countrylist.lastupdate + sevendays < datetime.now()):
            countrylistapi = listapi.query_countrylist()
            countrylist = CountryList({ country["name"] : country["iso_3166_1"] for country in countrylistapi })
            JsonSerializer().serialize_countrylist(countrylist)

        return countrylist
    
    def languages_get(self) -> CountryList:
        languagelist = JsonDeserializer().get_languagelist()

        sevendays = timedelta(days=7)
        if (not languagelist or languagelist.lastupdate + sevendays < datetime.now()):
            languagelistapi = listapi.query_languagelist()
            languagelist = LanguageList({ language["name"] : language["iso_639"] for language in languagelistapi })
            JsonSerializer().serialize_languagelist(languagelist)

        return languagelist
    
    def tags_get(self, filter:str=None) -> TagList:
        taglist = JsonDeserializer().get_taglist()

        sevendays = timedelta(days=7)
        if (not taglist or taglist.lastupdate + sevendays < datetime.now()):
            taglistapi = listapi.query_taglist()
            taglist = TagList([ tag["name"] for tag in taglistapi ])
            JsonSerializer().serialize_taglist(taglist)

        if filter:
            taglist.filter(filter)
            
        return taglist
    
    def favorites_add_stationtolist(self, stationuuid:UUID, favlistuuid:UUID) -> None:
        station = self.__radiostations.get_station(stationuuid)

        if not station:
            radiostationapi = stationapi.query_station(stationuuid)

            station = RadioStation(radiostationapi.stationuuid,
                                   radiostationapi.name,
                                   radiostationapi.url_resolved,
                                   radiostationapi.countrycode,
                                   radiostationapi.languagecodes,
                                   radiostationapi.homepage,
                                   None if utils.str_isnullorwhitespace(radiostationapi.favicon) else httpcontent.get_urlbinary_contentasb64(radiostationapi.favicon),
                                   None if utils.str_isnullorwhitespace(radiostationapi.favicon) else path.splitext(radiostationapi.favicon)[1][1:],
                                   radiostationapi.codec,
                                   radiostationapi.bitrate,
                                   list(radiostationapi.tags))
            
            self.__radiostations.add_station(station)
            JsonSerializer().serialize_radiostations(self.__radiostations)

        self.__favorites.get_list(favlistuuid).addstation(station)
        JsonSerializer().serialize_favorites(self.__favorites)

    def favorites_delete_stationfromlist(self, stationuuid:UUID, favlistuuid:UUID) -> None:
        station = self.__radiostations.get_station(stationuuid)

        self.__favorites.get_list(favlistuuid).removestation(station)
        JsonSerializer().serialize_favorites(self.__favorites)

        deletestation = True
        for favlist in self.__favorites.favoritelists:
            if station in favlist.stations:
                deletestation = False
                break

        if(deletestation):
            self.__radiostations.remove_station(station)
            JsonSerializer().serialize_radiostations(self.__radiostations)
    
    def favorites_getlists(self) -> tuple:
        return self.__favorites.favoritelists
    
    def favorites_addlist(self) -> FavoriteList:
        favoritelist = self.__favorites.add_favoritelist()
        JsonSerializer().serialize_favorites(self.__favorites)
        return favoritelist
    
    def favorites_deletelist(self, uuid:UUID) -> FavoriteList:
        self.__favorites.delete_favoritelist(uuid)
        JsonSerializer().serialize_favorites(self.__favorites)

    def favorites_getdefaultlist(self) -> FavoriteList:
        return self.__favorites.get_default()
    
    def favorites_getlist(self, listuuid:UUID) -> FavoriteList:
        return self.__favorites.get_list(listuuid)
    
    def favorites_changelistproperty(self, uuid:UUID, property:str, value:str):
        if property == "isdefault":
            self.__favorites.change_default(uuid, True if value.strip().lower() == "true" else False)
        elif property == "name":
            changelist = self.__favorites.get_list(uuid)
            changelist.name = value
        else: 
            raise TypeError(f"Change of property \"{property}\" supported.")
        
        JsonSerializer().serialize_favorites(self.__favorites)

    def get_serialzeduuids(self, uuids:list) -> str:
        return JsonSerializer().serialize_uuids(uuids)
    
    def get_serialzeduuid(self, uuid:UUID) -> str:
        return JsonSerializer().serialize_uuids(uuid)
    
    def get_serialzeddict(self, dict:dict) -> str:
        return JsonSerializer().serialize_dict(dict)