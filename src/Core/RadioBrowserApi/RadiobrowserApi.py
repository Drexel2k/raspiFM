import json
from .RequestBase import get_radiobrowser_post_request_data

def queryStationsAdvanced() -> list:
    stations = get_radiobrowser_post_request_data("/json/stations/search", {"name":"1live","countrycode":"DE","order":"votes","reverse":"true"})
    return json.loads(stations)