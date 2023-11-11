from . import requestbase
from ..json.jsonserialze import JsonSerialize

serializer = JsonSerialize()

def query_stations_advanced(name:str, countrycode:str, orderby:str, reverse:bool) -> dict:
    return serializer.get_dict_of_stations_advanced_response(requestbase.get_radiobrowser_post_request_data("/json/stations/search", {"name":name,"countrycode":countrycode,"order":orderby,"reverse":reverse}))