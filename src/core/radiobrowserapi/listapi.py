from . import requestbase
from ..json.JsonDeserializer import JsonDeserializer

def query_countrylist() -> dict:
    return JsonDeserializer().get_dict_from_response(requestbase.get_radiobrowser_post_request_data("/json/countries", {"order":"name","reverse":False}))

def query_languagelist() -> dict:
    return JsonDeserializer().get_dict_from_response(requestbase.get_radiobrowser_post_request_data("/json/languages", {"order":"name","reverse":False}))