
from datetime import datetime
from datetime import timedelta
from uuid import UUID

from .json.JsonSerializer import JsonSerializer
from .json.JsonDeserializer import JsonDeserializer
from .business.CountryList import CountryList
from .radiobrowserapi import stationapi
from .radiobrowserapi.data.RadioStationApi import RadioStationApi
from .radiobrowserapi import listapi
from .business.CountryList import CountryList
from .business.LanguageList import LanguageList
from .business.TagList import TagList
from .business.Favorites import Favorites
from .business.RadioStations import RadioStations
from .business.RadioStation import RadioStation
from ..utils import utils

from .raspifmsettings import serialization_directory


class RaspiFM:
    __slots__ = ["__favorites", "__radiostations"]
    __radiostations:RadioStations
    __favorites:Favorites

    def __init__(self):
        # Initialize Serializer
        JsonSerializer(serialization_directory)
        JsonDeserializer(serialization_directory)
        self.__radiostations = None
        self.__favorites = None

    @property
    def radiostations(self) -> RadioStations:
        if(not self.__radiostations):
            stations = JsonDeserializer().get_radiostations()
            if(not stations):
                stations = RadioStations()
            self.__radiostations = stations

        return self.__radiostations
    
    @property
    def favorites(self) -> Favorites:
        if(not self.__favorites):
            favorites = JsonDeserializer().get_favorites(self.radiostations)
            if(not favorites):
                favorites = Favorites()
            self.__favorites = favorites

        return self.__favorites

    def add_station_to_favlist(self, stationuuid:UUID, favlistuuid:UUID) -> None:
        station = self.radiostations.get_station(stationuuid)
        
        if not station:
            radiostationapi = stationapi.query_station(stationuuid)
            station = RadioStation(radiostationapi.stationuuid,
                                   radiostationapi.name,
                                   radiostationapi.url_resolved,
                                   radiostationapi.languagecodes,
                                   radiostationapi.homepage,
                                   None if utils.str_isnullorwhitespace(radiostationapi.favicon) else stationapi.get_faviconasb64(radiostationapi))
            
            self.radiostations.add_station(station)
            JsonSerializer().serialize_radiostations(self.radiostations)

        self.favorites.getlist(favlistuuid).addstation(station)
        JsonSerializer().serialize_favorites(self.favorites)

    def remove_station_from_favlist(self, stationuuid:UUID, favlistuuid:UUID) -> None:
        station = self.radiostations.get_station(stationuuid)

        self.favorites.getlist(favlistuuid).removestation(station)
        JsonSerializer().serialize_favorites(self.favorites)

        deletestation = True
        for favlist in self.favorites.favoritelists:
            if station in favlist.stations:
                deletestation = False
                break

        if(deletestation):
            self.radiostations.remove_station(station)
            JsonSerializer().serialize_radiostations(self.radiostations)
    
    def get_stations(self, name:str, country:str, language:str, tags:list, orderby:str, reverse:bool, page:int) -> list:
        return list(map(lambda radiostationdict: RadioStationApi(radiostationdict),
                   stationapi.query_stations_advanced(name, country, language, tags, orderby, reverse, page)))
    
    def get_countries(self) -> CountryList:
        countrylist = JsonDeserializer().get_countrylist()

        sevendays = timedelta(days=7)
        if (not countrylist or countrylist.lastupdate + sevendays < datetime.now()):
            countrylistapi = listapi.query_countrylist()
            countrylist = CountryList({ country["name"] : country["iso_3166_1"] for country in countrylistapi })
            JsonSerializer().serialize_countrylist(countrylist)

        return countrylist
    
    def get_languages(self) -> CountryList:
        languagelist = JsonDeserializer().get_languagelist()

        sevendays = timedelta(days=7)
        if (not languagelist or languagelist.lastupdate + sevendays < datetime.now()):
            languagelistapi = listapi.query_languagelist()
            languagelist = LanguageList({ language["name"] : language["iso_639"] for language in languagelistapi })
            JsonSerializer().serialize_languagelist(languagelist)

        return languagelist
    
    def get_tags(self, filter:str=None) -> TagList:
        taglist = JsonDeserializer().get_taglist()

        sevendays = timedelta(days=7)
        if (not taglist or taglist.lastupdate + sevendays < datetime.now()):
            taglistapi = listapi.query_taglist()
            taglist = TagList([ tag["name"] for tag in taglistapi ])
            JsonSerializer().serialize_taglist(taglist)

        if filter:
            taglist.filter(filter)
            
        return taglist




