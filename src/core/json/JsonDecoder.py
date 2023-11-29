from datetime import datetime
import json
from uuid import UUID

from ..business.CountryList import CountryList
from ..business.FavoriteList import FavoriteList
from ..business.Favorites import Favorites
from ..business.LanguageList import LanguageList
from ..business.RadioStation import RadioStation
from ..business.RadioStations import RadioStations
from ..business.TagList import TagList

class CountryListDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if "__type__" in obj and obj["__type__"] == "CountryList":
            obj["lastupdate"] =  datetime.fromisoformat(obj["lastupdate"])
            return CountryList(serializationdata=obj)
        
        return obj
    
class FavoriteListDecoder(json.JSONDecoder):
    __slots__ = ["__radiostations"]
    __radiostations:RadioStations

    def __init__(self, **kwargs):
        self.__radiostations = kwargs["stations"]
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, obj):
        if "__type__" in obj and obj["__type__"] == "FavoriteList":
            obj["uuid"] = UUID(obj["uuid"])

            stations = []
            for stationuuid in obj["stations"]:
                station = next((station for station in self.__radiostations.stationlist if station.uuid == UUID(stationuuid)), None)
                if(not station):
                    raise TypeError("Station in FavoriteList does not exist in Radiostations.")
                stations.append(station)

            obj["stations"] = stations

            return FavoriteList(serializationdata=obj)
        
        return obj
    
class FavoritesDecoder(json.JSONDecoder):
    __slots__ = ["__radiostations"]
    __radiostations:RadioStations

    def __init__(self, **kwargs):
        self.__radiostations = kwargs["stations"]
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, obj):
        if "__type__" in obj and obj["__type__"] == "Favorites":
            return Favorites(serializationdata=obj)
        
        if "__type__" in obj and obj["__type__"] == "FavoriteList":
            return FavoriteListDecoder(stations=self.__radiostations).object_hook(obj)
        
        return obj
    
class LanguageListDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, obj):
        if "__type__" in obj and obj["__type__"] == "LanguageList":
            obj["lastupdate"] =  datetime.fromisoformat(obj["lastupdate"])
            return LanguageList(serializationdata=obj)
        
        return obj
    
class RadioStationDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, obj):
        if "__type__" in obj and obj["__type__"] == "RadioStation":
            obj["uuid"] = UUID(obj["uuid"])
            return RadioStation(serializationdata=obj)
        
        return obj
    
class RadioStationsDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, obj):
        if "__type__" in obj and obj["__type__"] == "RadioStations":
            return RadioStations(serializationdata=obj)
        
        if "__type__" in obj and obj["__type__"] == "RadioStation":
            return RadioStationDecoder().object_hook(obj)
        
        return obj
    
class TagListDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, obj):
        if "__type__" in obj and obj["__type__"] == "TagList":
            obj["lastupdate"] =  datetime.fromisoformat(obj["lastupdate"])
            return TagList(serializationdata=obj)
        
        return obj