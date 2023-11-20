import json
from uuid import UUID

from ..business.RadioStations import RadioStations
from ..business.FavoriteList import FavoriteList

class FavoriteListEncoder(json.JSONEncoder):
    def default(self, obj:FavoriteList):
        if isinstance(obj, FavoriteList):
             return {"__type__":"FavoriteList", "uuid":str(obj.uuid), "name":obj.name, "isdefault":obj.isdefault, "stations":[str(station.uuid) for station in obj.stations]}
    
        return json.JSONEncoder.default(self, obj)
        
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
                    raise TypeError("Station in FavoriteList does not exist in Radiostatiosn.")
                stations.append(station)

            obj["stations"] = stations

            return FavoriteList(serializationdata=obj)
        
        return obj
    
