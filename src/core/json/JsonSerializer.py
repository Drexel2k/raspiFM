from __future__ import annotations
import json
from pathlib import Path

from .CountryListSerialization import CountryListEncoder
from .LanguageListSerialization import LanguageListEncoder
from .FavoritesSerialization import FavoritesEncoder
from .TagListSerialization import TagListEncoder
from ..business.CountryList import CountryList
from ..business.LanguageList import LanguageList
from ..business.TagList import TagList
from ..business.Favorites import Favorites
from ..business.RadioStations import RadioStations
from .RestParamsSerialization import RestParamsEncoder
from .RadioStationsSerialization import RadioStationsEncoder


class JsonSerializer():
    __slots__ = ["__path"]
    __instance:JsonSerializer  = None
    __path:str

    def __new__(cls, *path):
        if cls.__instance is None:
            if not path:
                raise TypeError("On first call a path paramter must be given which is the serialization folder.")

            cls.__instance = super(JsonSerializer, cls).__new__(cls)
            cls.__instance.__init(path[0])
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

    def serialize_restparams(self, params:dict) -> str:
        return json.dumps(params, cls=RestParamsEncoder).encode("utf-8")
