from src.core.radiobrowserapi import requestbase

def query_stations_advanced() -> list:
    stations = requestbase.get_radiobrowser_post_request_data("/json/stations/search", {"name":"1live","countrycode":"DE","order":"votes","reverse":"true"})
    return stations