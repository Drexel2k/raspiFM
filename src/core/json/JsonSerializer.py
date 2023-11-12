from __future__ import annotations
import json
from pathlib import Path
from .CountryListSerialization import CountryListEncoder
from ..business.CountryList import CountryList

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
    
    def serialize_countrylist(self, countrylist: CountryList) -> None:
        with open(Path(self.__path, "cache/countrylist.json"), "w+") as outfile:
            outfile.write(json.dumps(countrylist, cls=CountryListEncoder , indent=4))