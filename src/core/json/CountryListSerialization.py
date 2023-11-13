import json
from datetime import datetime
from ..business.CountryList import CountryList

class CountryListEncoder(json.JSONEncoder):
        def default(self, obj:CountryList):
            return {"lastupdate":obj.lastupdate.isoformat(), "countrylist":obj.countrylist}
        
class CountryListDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
    def object_hook(self, dct):
        return CountryList(dct["countrylist"], datetime.fromisoformat(dct["lastupdate"]))
