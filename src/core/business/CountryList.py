from __future__ import annotations
from datetime import datetime

class CountryList:
    __slots__ = ["__lastupdate", "__countrylist"]
    __lastupdate:datetime

    #Key is name, value is code to unify with LanguageList, see LanguageList
    __countrylist:dict

    @property
    def lastupdate(self) -> datetime:
        return self.__lastupdate
    
    @property
    def countrylist(self) -> dict:
        return self.__countrylist

    @classmethod
    def from_default(cls, countrylist:list) -> CountryList:
        if(not countrylist):
            raise ValueError("countrylist must not be null for CountryList.")
        
        obj = cls()
        obj.__setattr__("_CountryList__countrylist", countrylist)
        obj.__setattr__("_CountryList__lastupdate", datetime.now())
        return obj

    @classmethod
    def deserialize(cls, serializationdata:dict) -> CountryList:
        if (not serializationdata):
            raise TypeError("Argument serializationdata must be given for CountryList deserialization.")

        obj = cls()

        for slot in cls.__slots__:
            dictkey = slot[2:]
            if(not(dictkey in serializationdata)):
                raise TypeError(f"{dictkey} key not found in CountryList serialization data.")
            
            obj.__setattr__(f"_CountryList{slot}", serializationdata[dictkey])

        return obj
