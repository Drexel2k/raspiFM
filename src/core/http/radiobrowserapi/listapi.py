from core.http.radiobrowserapi import requestbase
from core.json.JsonDeserializer import JsonDeserializer

def query_countrylist() -> dict:
    return JsonDeserializer().get_dict_from_response(requestbase.get_radiobrowser_post_request_data("/json/countries", {"order":"name","reverse":False}))

def query_languagelist() -> dict:
    return JsonDeserializer().get_dict_from_response(requestbase.get_radiobrowser_post_request_data("/json/languages", {"order":"name","reverse":False}))

def query_taglist() -> dict:
    return JsonDeserializer().get_dict_from_response(requestbase.get_radiobrowser_post_request_data("/json/tags", {"order":"name","reverse":False}))