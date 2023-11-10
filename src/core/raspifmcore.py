#Entry to call Core functions directly with launch config
import json

from src.core.radiobrowserapi import stationapi
data = stationapi.query_stations_advanced()
print(json.dumps(json.loads(data)))


