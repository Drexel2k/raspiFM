import json
from uuid import UUID

class RestParamsEncoder(json.JSONEncoder):
    def default(self, obj:dict):
        if isinstance(obj, UUID):
            return str(obj)
        
        return json.JSONEncoder.default(self, obj)
