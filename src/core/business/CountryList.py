from datetime import datetime

class CountryList:
    __slots__ = ["__lastupdate", "__countrylist"]
    __lastupdate:datetime
    __countrylist:dict

    @property
    def lastupdate(self):
        return self.__lastupdate
    
    @property
    def countrylist(self):
        return self.__countrylist

    def __init__(self, countrylist:dict, lastupdate:datetime=datetime.now()):
        self.__lastupdate = lastupdate
        self.__countrylist = countrylist




