import json
from uuid import UUID
from ..business.RadioStations import RadioStation

class RadioStationEncoder(json.JSONEncoder):
    def default(self, obj:RadioStation):
        if isinstance(obj, RadioStation):
            return {"__type__":"RadioStation", "uuid":str(obj.uuid), "name":obj.name, "url":obj.url, "languagecodes":obj.languacecodes, "homepage":obj.homepage, "faviconb64":obj.faviconb64}    
    
        return json.JSONEncoder.default(self, obj)

class RadioStationDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, obj):
        if "__type__" in obj and obj["__type__"] == "RadioStation":
            obj["uuid"] = UUID(obj["uuid"])
            return RadioStation(serializationdata=obj)
        
        return obj