import json
from ..business.RadioStations import RadioStations
from ..business.RadioStation import RadioStation
from .RadioStationSerialization import RadioStationEncoder
from .RadioStationSerialization import RadioStationDecoder

class RadioStationsEncoder(json.JSONEncoder):
    def default(self, obj:RadioStations):
        if isinstance(obj, RadioStations):
            return {"__type__":"RadioStations", "stationlist":obj.stationlist}
        
        if isinstance(obj, RadioStation):
                return RadioStationEncoder().default(obj)
    
        return json.JSONEncoder.default(self, obj)
    
class RadioStationsDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, obj):
        if "__type__" in obj and obj["__type__"] == "RadioStations":
            return RadioStations(serializationdata=obj)
        
        if "__type__" in obj and obj["__type__"] == "RadioStation":
            return RadioStationDecoder().object_hook(obj)
        
        return obj