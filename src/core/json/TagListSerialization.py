import json
from datetime import datetime
from ..business.TagList import TagList

class TagListEncoder(json.JSONEncoder):
        def default(self, obj:TagList):
            return {"__type__":"TagList", "lastupdate":obj.lastupdate.isoformat(), "taglist":obj.taglist}
        
class TagListDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
    def object_hook(self, dct):
        if "__type__" in dct and dct["__type__"] == "TagList":
            return TagList(dct["taglist"], datetime.fromisoformat(dct["lastupdate"]))
        
        return dct
