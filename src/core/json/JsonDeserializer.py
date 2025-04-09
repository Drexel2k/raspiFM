from __future__ import annotations
import json
from pathlib import Path

from core.json.JsonDecoder import CountryListDecoder, UserSettingsDecoder, LanguageListDecoder, TagListDecoder, FavoritesDecoder, RadioStationsDecoder
from core.Settings import UserSettings
from core.business.CountryList import CountryList
from core.business.LanguageList import LanguageList
from core.business.TagList import TagList
from core.business.Favorites import Favorites
from core.business.RadioStations import RadioStations

class JsonDeserializer():
    __slots__ = ["__path"]
    __instance:JsonDeserializer  = None
    __path:str

    def __new__(cls, path = None):
        if cls.__instance is None:
            if path is None:
                raise TypeError("On first call a path parameter must be given which is the serialization folder.")

            cls.__instance = super(JsonDeserializer, cls).__new__(cls)
            cls.__instance.__init(path)
        return cls.__instance
    
    def __init(self, path:str):
        self.__path = path
    
    def get_countrylist(self) -> CountryList:
        if Path(self.__path, "cache/countrylist.json").exists():
            with open(Path(self.__path, "cache/countrylist.json"), "r") as infile:
                jsonstring = infile.read()
                if not jsonstring is None:
                    return json.loads(jsonstring, cls=CountryListDecoder)
            
        return None
        
    def get_languagelist(self) -> LanguageList:
        if Path(self.__path, "cache/languagelist.json").exists():
            with open(Path(self.__path, "cache/languagelist.json"), "r") as infile:
                jsonstring = infile.read()
                if not jsonstring is None:
                    return json.loads(jsonstring, cls=LanguageListDecoder)
            
        return None

    def get_taglist(self) -> TagList:
        if Path(self.__path, "cache/taglist.json").exists():
            with open(Path(self.__path, "cache/taglist.json"), "r") as infile:
                jsonstring = infile.read()
                if not jsonstring is None:
                    return json.loads(jsonstring, cls=TagListDecoder)
            
        return None
        
    def get_favorites(self, stations:RadioStations) -> Favorites:
        if Path(self.__path, "favorites.json").exists():
            with open(Path(self.__path, "favorites.json"), "r") as infile:
                jsonstring = infile.read()
                if not jsonstring is None:
                    return json.loads(jsonstring, cls=FavoritesDecoder, stations=stations)
            
        return None
    
    def get_radiostations(self) -> RadioStations:
        if Path(self.__path, "radiostations.json").exists():
            with open(Path(self.__path, "radiostations.json"), "r") as infile:
                jsonstring = infile.read()
                if not jsonstring is None:
                    return json.loads(jsonstring, cls=RadioStationsDecoder)
            
        return None
    
    def get_usersettings(self) -> UserSettings:
        if Path(self.__path, "settings.json").exists():
            with open(Path(self.__path, "settings.json"), "r") as infile:
                jsonstring = infile.read()
                if not jsonstring is None:
                    return json.loads(jsonstring, cls=UserSettingsDecoder)
            
        return None