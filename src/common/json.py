import json
import io
from uuid import UUID

def deserialize_from_string_or_bytes(jsons_content:str|bytes|bytearray, encoding=None) -> dict:
    if encoding is None:
        return json.loads(jsons_content)
    else:
        tiow = io.TextIOWrapper(io.BytesIO(jsons_content), encoding=encoding, newline="")
        obj = json.load(tiow)
        tiow.close()
        return obj
    
def serialize_to_string_or_bytes(dict_content:dict, encoding=None) -> str|bytes:
    if encoding is None:
        return json.dumps(dict_content)
    else:
        return json.dumps(dict_content, ensure_ascii=False).encode(encoding)

def serialize_uuids(uuids:list) -> str:
    return json.dumps(uuids, default=str)

def serialize_uuid(uuid:UUID) -> str:
    return json.dumps(uuid, default=str)

class DictEncoder(json.JSONEncoder):
    def default(self, obj:dict):
        if isinstance(obj, UUID):
            return str(obj)
        
        return json.JSONEncoder.default(self, obj)
    
def serialize_dict(dictionary:dict) -> str:
    return json.dumps(dictionary, cls=DictEncoder)