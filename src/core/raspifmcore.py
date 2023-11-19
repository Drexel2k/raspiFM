
from datetime import datetime
from datetime import timedelta

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

from .raspifmsettings import serialization_directory


class RaspiFM:
    def __init__(self):
        # Initialize Serializer
        JsonSerializer(serialization_directory)
        JsonDeserializer(serialization_directory)

    def get_favorites(self) -> dict:
        favorites = JsonDeserializer().get_favorites()
        if(not favorites):
            favorites = Favorites()

        return favorites

    def add_station_to_favorites(self, favoriteList, station):
        raise NotImplementedError
    
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




