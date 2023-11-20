from uuid import UUID

from . import requestbase
from ..radiobrowserapi.data.RadioStationApi import RadioStationApi
from ..json.JsonDeserializer import JsonDeserializer

def query_stations_advanced(name:str, country:str, language:str, tags:list, orderby:str, reverse:bool, page:int) -> dict:
    return JsonDeserializer().get_dict_from_response(
        requestbase.get_radiobrowser_post_request_data("/json/stations/search",
                                                       {"name":name,
                                                        "countrycode":country,
                                                        "language":language,
                                                        "tagList":tags,
                                                        "tagExact":True,
                                                        "order":orderby,
                                                        "reverse":reverse,
                                                        "offset":(page - 1) * 20,
                                                        "limit":20,
                                                        "hidebroken":True}))

def query_station(stationuuid:UUID) -> RadioStationApi:
    
    return RadioStationApi(JsonDeserializer().get_dict_from_response(
        requestbase.get_radiobrowser_post_request_data("/json/stations/byuuid",
                                                       {"uuids":stationuuid}))[0])

def get_faviconasb64(station:RadioStationApi) -> str:
    return requestbase.get_urlbinary_contentasb64(station.favicon)