import json
from datetime import datetime
from ..business.LanguageList import LanguageList

class LanguageListEncoder(json.JSONEncoder):
    def default(self, obj:LanguageList):
        if isinstance(obj, LanguageList):
            return {"__type__":"LanguageList", "lastupdate":obj.lastupdate.isoformat(), "languagelist":obj.languagelist}
    
        return json.JSONEncoder.default(self, obj)            
                
class LanguageListDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, obj):
        if "__type__" in obj and obj["__type__"] == "LanguageList":
            obj["lastupdate"] =  datetime.fromisoformat(obj["lastupdate"])
            return LanguageList(serializationdata=obj)
        
        return obj
