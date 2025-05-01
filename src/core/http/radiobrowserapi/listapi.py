from core.http.radiobrowserapi import requestbase
from common import json

def query_countrylist() -> dict:
    return json.deserialize_from_string_or_bytes(requestbase.get_radiobrowser_post_request_data("/json/countries", {"order":"name","reverse":False}))

def query_languagelist() -> dict:
    return json.deserialize_from_string_or_bytes(requestbase.get_radiobrowser_post_request_data("/json/languages", {"order":"name","reverse":False}))

def query_taglist() -> dict:
    return json.deserialize_from_string_or_bytes(requestbase.get_radiobrowser_post_request_data("/json/tags", {"order":"name","reverse":False}))