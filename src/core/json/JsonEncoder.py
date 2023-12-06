import json
from uuid import UUID

from ..Settings import UserSettings
from ..business.CountryList import CountryList
from ..business.FavoriteList import FavoriteList
from ..business.Favorites import Favorites
from ..business.LanguageList import LanguageList
from ..business.RadioStation import RadioStation
from ..business.RadioStations import RadioStations
from ..business.TagList import TagList

class CountryListEncoder(json.JSONEncoder):
    def default(self, obj:CountryList):
        if isinstance(obj, CountryList):
             return {"__type__":"CountryList", "lastupdate":obj.lastupdate.isoformat(), "countrylist":obj.countrylist}
    
        return json.JSONEncoder.default(self, obj)
    
class FavoriteListEncoder(json.JSONEncoder):
    def default(self, obj:FavoriteList):
        if isinstance(obj, FavoriteList):
             return {"__type__":"FavoriteList", "uuid":str(obj.uuid), "name":obj.name, "isdefault":obj.isdefault, "stations":[str(station.uuid) for station in obj.stations]}
    
        return json.JSONEncoder.default(self, obj)
    
class FavoritesEncoder(json.JSONEncoder):
    def default(self, obj:Favorites):
        if isinstance(obj, Favorites):
            return {"__type__":"Favorites", "favoritelists":obj.favoritelists}
        
        if isinstance(obj, FavoriteList):
            return FavoriteListEncoder().default(obj)
    
        return json.JSONEncoder.default(self, obj)
    
class LanguageListEncoder(json.JSONEncoder):
    def default(self, obj:LanguageList):
        if isinstance(obj, LanguageList):
            return {"__type__":"LanguageList", "lastupdate":obj.lastupdate.isoformat(), "languagelist":obj.languagelist}
    
        return json.JSONEncoder.default(self, obj)
    
class RadioStationEncoder(json.JSONEncoder):
    def default(self, obj:RadioStation):
        if isinstance(obj, RadioStation):
            return {"__type__":"RadioStation", "uuid":str(obj.uuid), "name":obj.name, "url":obj.url, "countrycode":obj.countrycode, "languagecodes":obj.languacecodes, "homepage":obj.homepage, "faviconb64":obj.faviconb64, "faviconextension":obj.faviconextension, "codec":obj.codec, "bitrate":obj.bitrate, "tags":obj.tags}    
    
        return json.JSONEncoder.default(self, obj)
    
class RadioStationsEncoder(json.JSONEncoder):
    def default(self, obj:RadioStations):
        if isinstance(obj, RadioStations):
            return {"__type__":"RadioStations", "stationlist":obj.stationlist}
        
        if isinstance(obj, RadioStation):
                return RadioStationEncoder().default(obj)
    
        return json.JSONEncoder.default(self, obj)
    
class TagListEncoder(json.JSONEncoder):
    def default(self, obj:TagList):
        if isinstance(obj, TagList):
            return {"__type__":"TagList", "lastupdate":obj.lastupdate.isoformat(), "taglist":obj.taglist}
    
        return json.JSONEncoder.default(self, obj)
    
class UserSettingsEncoder(json.JSONEncoder):
    def default(self, obj:UserSettings):
        if isinstance(obj, UserSettings):
            return {"__type__":"UserSettings", "web_defaultlanguage":obj.web_defaultlanguage, "web_defaultcountry":obj.web_defaultcountry, "touch_runontouch":obj.touch_runontouch}
    
        return json.JSONEncoder.default(self, obj)
    
class RestParamsEncoder(json.JSONEncoder):
    def default(self, obj:dict):
        if isinstance(obj, UUID):
            return str(obj)
        
        return json.JSONEncoder.default(self, obj)