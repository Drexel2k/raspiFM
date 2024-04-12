from uuid import UUID

from core.http.radiobrowserapi import requestbase
from core.http.radiobrowserapi.data.RadioStationApi import RadioStationApi
from core.json.JsonDeserializer import JsonDeserializer

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

def send_stationclicked(stationuuid:UUID) -> None:
    requestbase.radiobrowser_get_request("/json", {"url":str(stationuuid)})