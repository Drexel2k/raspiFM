from . import requestbase
from ..json.JsonDeserializer import JsonDeserializer

def query_stations_advanced(name:str, country:str, language:str, orderby:str, reverse:bool) -> dict:
    return JsonDeserializer().get_dict_from_response(
        requestbase.get_radiobrowser_post_request_data("/json/stations/search",
                                                       {"name":name,
                                                        "countrycode":country,
                                                        "language":language,
                                                        "order":orderby,
                                                        "reverse":reverse}))