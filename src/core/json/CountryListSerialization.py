import json
from datetime import datetime
from ..business.CountryList import CountryList

class CountryListEncoder(json.JSONEncoder):
    def default(self, obj:CountryList):
        if isinstance(obj, CountryList):
             return {"__type__":"CountryList", "lastupdate":obj.lastupdate.isoformat(), "countrylist":obj.countrylist}
    
        return json.JSONEncoder.default(self, obj)
               
class CountryListDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if "__type__" in obj and obj["__type__"] == "CountryList":
            obj["lastupdate"] =  datetime.fromisoformat(obj["lastupdate"])
            return CountryList(serializationdata=obj)
        
        return obj
