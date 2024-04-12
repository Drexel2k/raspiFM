from datetime import datetime
import json
from uuid import UUID

from core.Settings import UserSettings
from core.business.CountryList import CountryList
from core.business.FavoriteList import FavoriteList
from core.business.Favorites import Favorites
from core.business.LanguageList import LanguageList
from core.business.RadioStation import RadioStation
from core.business.RadioStations import RadioStations
from core.business.TagList import TagList
from core.business.ViewProxies.RadioStationFavoriteEntry import RadioStationFavoriteEntry
from core.StartWith import StartWith

class CountryListDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if "__type__" in obj and obj["__type__"] == "CountryList":
            obj["lastupdate"] =  datetime.fromisoformat(obj["lastupdate"])
            return CountryList.deserialize(obj)
        
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
            obj["stations"] = [RadioStationFavoriteEntry(self.__radiostations.get_station(UUID(stationentry["stationuuid"])), stationentry["displayorder"]) for stationentry in obj["stations"]]
            return FavoriteList.deserialize(obj)

        return obj

class FavoritesDecoder(json.JSONDecoder):
    __slots__ = ["__radiostations"]
    __radiostations:RadioStations

    def __init__(self, **kwargs):
        self.__radiostations = kwargs["stations"]
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, obj):
        if "__type__" in obj and obj["__type__"] == "Favorites":
            return Favorites.deserialize(obj)
        
        if "__type__" in obj and obj["__type__"] == "FavoriteList":
            return FavoriteListDecoder(stations=self.__radiostations).object_hook(obj)
        
        return obj
    
class LanguageListDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, obj):
        if "__type__" in obj and obj["__type__"] == "LanguageList":
            obj["lastupdate"] =  datetime.fromisoformat(obj["lastupdate"])
            return LanguageList.deserialize(obj)
        
        return obj
    
class RadioStationDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, obj):
        if "__type__" in obj and obj["__type__"] == "RadioStation":
            obj["uuid"] = UUID(obj["uuid"])
            return RadioStation.deserialize(obj)
        
        return obj
    
class RadioStationsDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, obj):
        if "__type__" in obj and obj["__type__"] == "RadioStations":
            return RadioStations.deserialize(obj)
        
        if "__type__" in obj and obj["__type__"] == "RadioStation":
            return RadioStationDecoder().object_hook(obj)
        
        return obj
    
class TagListDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, obj):
        if "__type__" in obj and obj["__type__"] == "TagList":
            obj["lastupdate"] =  datetime.fromisoformat(obj["lastupdate"])
            return TagList.deserialize(obj)
        
        return obj
    
class UserSettingsDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, obj):
        if "__type__" in obj and obj["__type__"] == "UserSettings":
            obj["touch_startwith"] =  StartWith[obj["touch_startwith"]]
            obj["touch_laststation"] = UUID(obj["touch_laststation"]) if obj["touch_laststation"] else None
            return UserSettings.deserialize(obj)
        
        return obj