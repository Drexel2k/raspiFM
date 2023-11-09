import json
import os
from RadioBrowserApi.RadiobrowserApi import queryStationsAdvanced

data = queryStationsAdvanced()
print(type(data))
print(json.dumps(data, indent=4))

path = "home/raspifm/raspifm"
if not (os.path.exists(path) and os.path.isdir(path)):
   os.makedirs(path)

path = f"{ path }/sample.json"
with open(path, "w") as outfile:
    json.dump(data, outfile, indent=4)