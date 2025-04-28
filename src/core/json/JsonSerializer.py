from __future__ import annotations
import json
from pathlib import Path

from core.json.JsonEncoder import CountryListEncoder, UserSettingsEncoder, LanguageListEncoder, FavoritesEncoder, TagListEncoder
from core.Settings import UserSettings
from core.business.CountryList import CountryList
from core.business.LanguageList import LanguageList
from core.business.TagList import TagList
from core.business.Favorites import Favorites
from core.business.RadioStations import RadioStations
from core.json.JsonEncoder import RestParamsEncoder, RadioStationsEncoder

class JsonSerializer:
    __slots__ = ["__path"]
    __instance:JsonSerializer = None
    __path:str

    def __new__(cls, path = None):
        if cls.__instance is None:
            if path is None:
                raise ValueError("Missing argument on first call (initialization): path")

            cls.__instance = super(JsonSerializer, cls).__new__(cls)
            cls.__instance.__init(path)
        return cls.__instance
    
    def __init(self, path:str):
        self.__path = path
    
    def serialize_countrylist(self, countrylist:CountryList) -> None:
        with open(Path(self.__path, "cache/countrylist.json"), "w+") as outfile:
            outfile.write(json.dumps(countrylist, cls=CountryListEncoder , indent=4))

    def serialize_languagelist(self, languagelist:LanguageList) -> None:
        with open(Path(self.__path, "cache/languagelist.json"), "w+") as outfile:
            outfile.write(json.dumps(languagelist, cls=LanguageListEncoder , indent=4))

    def serialize_taglist(self, taglist:TagList) -> None:
        with open(Path(self.__path, "cache/taglist.json"), "w+") as outfile:
            outfile.write(json.dumps(taglist, cls=TagListEncoder , indent=4))
    
    def serialize_radiostations(self, radiostations:RadioStations) -> None:
        with open(Path(self.__path, "radiostations.json"), "w+") as outfile:
            outfile.write(json.dumps(radiostations, cls=RadioStationsEncoder, indent=4))

    def serialize_favorites(self, favorites:Favorites) -> None:
        with open(Path(self.__path, "favorites.json"), "w+") as outfile:
            outfile.write(json.dumps(favorites, cls=FavoritesEncoder ,indent=4))

    def serialize_usersettings(self, usersettings:UserSettings) -> None:
        with open(Path(self.__path, "settings.json"), "w+") as outfile:
            outfile.write(json.dumps(usersettings, cls=UserSettingsEncoder, indent=4))