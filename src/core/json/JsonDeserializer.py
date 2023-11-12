from __future__ import annotations
import json
from pathlib import Path

from .CountryListSerialization import CountryListDecoder
from ..business.CountryList import CountryList

class JsonDeserializer():
    __slots__ = ["__path"]
    __instance:JsonDeserializer  = None
    __path:str

    def __new__(cls, *path):
        if cls.__instance is None:
            if not path:
                raise TypeError("On first call a path paramter must be given which is the serialization folder.")

            cls.__instance = super(JsonDeserializer, cls).__new__(cls)
            cls.__instance.__init(path[0])
        return cls.__instance
    
    def __init(self, path:str):
        self.__path = path

    def get_dict_from_response(self, jsonstring:str) -> dict:
        return json.loads(jsonstring)
    
    def get_countrylist(self) -> CountryList:
        d1 = Path(self.__path, "cache/countrylist.json")
        if Path(self.__path, "cache/countrylist.json").exists():
            with open(Path(self.__path, "cache/countrylist.json"), "r") as infile:
                jsonstring = infile.read()
                if jsonstring:
                    return json.loads(jsonstring, cls=CountryListDecoder)
            
            return None