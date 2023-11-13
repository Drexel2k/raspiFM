import json
from datetime import datetime
from ..business.LanguageList import LanguageList

class LanguageListEncoder(json.JSONEncoder):
        def default(self, obj:LanguageList):
            return {"__type__":"LanguageList", "lastupdate":obj.lastupdate.isoformat(), "languagelist":obj.languagelist}
        
class LanguageListDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
    def object_hook(self, dct):
        if "__type__" in dct and dct["__type__"] == "LanguageList":
            return LanguageList(dct["languagelist"], datetime.fromisoformat(dct["lastupdate"]))
        
        return dct
