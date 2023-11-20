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

    def __init__(self, countrylist:list=None, serializationdata:dict=None):
        if(serializationdata):
            self.__countrylist = {}
            for slot in enumerate(self.__slots__):
                dictkey = slot[1][2:]
                if(not(dictkey in serializationdata)):
                    raise TypeError(f"{dictkey} key not found in CountryList serialization data.")
                
                self.__setattr__(f"_CountryList{slot[1]}", serializationdata[dictkey])
        else:
            if(not countrylist):
                raise ValueError("countrylist must not be null for CountryList.")
            
            self.__lastupdate = datetime.now()
            self.__countrylist = dict(sorted(countrylist.items()))


