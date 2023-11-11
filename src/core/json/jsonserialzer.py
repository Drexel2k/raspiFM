from __future__ import annotations
import json

class JsonSerializer():
    __slots__ = ["__path"]
    __instance:JsonSerializer  = None
    __path:str

    def __new__(cls, *path):
        if cls.__instance is None:
            if not path:
                raise TypeError("On first call a path paramter must be given which is the serialization folder.")

            cls.__instance = super(JsonSerializer, cls).__new__(cls)
            cls.__instance.__path = path[0]
        return cls.__instance
    
    def get_dict_of_stations_advanced_response(self, jsonstring:str) -> dict:
        return json.loads(jsonstring)