
from datetime import datetime
from datetime import timedelta
from .json.JsonSerializer import JsonSerializer
from .json.JsonDeserializer import JsonDeserializer
from .business.CountryList import CountryList
from .radiobrowserapi import stationapi
from .radiobrowserapi.data.RadioStationApi import RadioStationApi
from .radiobrowserapi import listapi
from.raspifmsettings import serialization_directory


class RaspiFM:
    def __init__(self):
        # Initialize Serializer
        JsonSerializer(serialization_directory)
        JsonDeserializer(serialization_directory)

    def get_Favorites(self):
        raise NotImplementedError

    def add_station_to_favorites(self, favoriteList, station):
        raise NotImplementedError
    
    def get_stations(self, name:str, countrycode:str, orderby:str, reverse:bool) -> map:
        return map(lambda radiostationdict: RadioStationApi(radiostationdict),
                   stationapi.query_stations_advanced(name, countrycode, orderby, reverse))
    
    def get_countries(self) -> CountryList:
        countrylist = JsonDeserializer().get_countrylist()

        sevendays = timedelta(days=7)
        if (not countrylist or countrylist.lastupdate + sevendays < datetime.now()):
            countrylist = CountryList(list(map(lambda countrylistdict: countrylistdict["iso_3166_1"], listapi.query_countrylist())))
            JsonSerializer().serialize_countrylist(countrylist)

        return countrylist



