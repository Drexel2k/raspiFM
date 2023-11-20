import json
from datetime import datetime
from ..business.TagList import TagList

class TagListEncoder(json.JSONEncoder):
    def default(self, obj:TagList):
        if isinstance(obj, TagList):
            return {"__type__":"TagList", "lastupdate":obj.lastupdate.isoformat(), "taglist":obj.taglist}
    
        return json.JSONEncoder.default(self, obj)

class TagListDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, obj):
        if "__type__" in obj and obj["__type__"] == "TagList":
            obj["lastupdate"] =  datetime.fromisoformat(obj["lastupdate"])
            return TagList(serializationdata=obj)
        
        return obj
