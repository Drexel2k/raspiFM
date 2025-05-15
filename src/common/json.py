import io
import json
from json import JSONEncoder
from uuid import UUID
from typing import Type

def deserialize_from_string_or_bytes(jsons_content:str|bytes|bytearray, encoding=None) -> dict:
    if encoding is None:
        return json.loads(jsons_content)
    else:
        return json.loads(jsons_content.decode(encoding))
    
def serialize_to_string_or_bytes(content:any, encoding=None, encoder:Type=None) -> bytes:
    if encoding is None and encoder is None:
        return json.dumps(content)
    if not encoding is None and not encoder is None:
        return json.dumps(content, ensure_ascii=False, cls=encoder).encode(encoding)
    if not encoding is None:
        return json.dumps(content, ensure_ascii=False).encode(encoding)
    if not encoder is None:
        return json.dumps(content, ensure_ascii=False, cls=encoder)

class UUIDEncoder(JSONEncoder):
    def default(self, obj:dict):
        if isinstance(obj, UUID):
            return str(obj)
        
        return json.JSONEncoder.default(self, obj)