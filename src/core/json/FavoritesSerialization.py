import json

from ..business.RadioStations import RadioStations
from ..business.Favorites import Favorites
from ..business.FavoriteList import FavoriteList
from .FavoriteListSerialization import FavoriteListEncoder
from .FavoriteListSerialization import FavoriteListDecoder

class FavoritesEncoder(json.JSONEncoder):
    def default(self, obj:Favorites):
        if isinstance(obj, Favorites):
            return {"__type__":"Favorites", "favoritelists":obj.favoritelists}
        
        if isinstance(obj, FavoriteList):
            return FavoriteListEncoder().default(obj)
    
        return json.JSONEncoder.default(self, obj)

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
