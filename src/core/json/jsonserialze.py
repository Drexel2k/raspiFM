import json

class JsonSerialize:
    __slots__ = []

    def __init__(self):
        pass

    def get_dict_of_stations_advanced_response(self, jsonstring:str) -> dict:
       return json.loads(jsonstring)