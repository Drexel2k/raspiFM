from datetime import datetime

class CountryList:
    __slots__ = ["__lastupdate", "__countrylist"]
    __lastupdate:datetime
    __countrylist:dict

    @property
    def lastupdate(self) -> datetime:
        return self.__lastupdate
    
    @property
    def countrylist(self) -> dict:
        return self.__countrylist

    def __init__(self, countrylist:dict, lastupdate:datetime=datetime.now()):
        self.__lastupdate = lastupdate
        self.__countrylist = dict(sorted(countrylist.items()))




