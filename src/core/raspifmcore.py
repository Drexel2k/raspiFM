from .business.RadioStation import RadioStation
from .radiobrowserapi import stationapi

class RaspiFM:
    __slots__ = ["jsonserialize"]

    def __init__(self):
        pass

    def get_Favorites(self):
        raise NotImplementedError

    def add_station_to_favorites(self, favoriteList, station):
        raise NotImplementedError
    
    def get_stations(self, name:str, countrycode:str, orderby:str, reverse:bool) -> list[RadioStation]:
        return map(lambda radiostationdict: RadioStation(radiostationdict["stationuuid"], radiostationdict["name"], radiostationdict["url"], radiostationdict["languagecodes"], radiostationdict["homepage"]),
                   stationapi.query_stations_advanced(name, countrycode, orderby, reverse))



