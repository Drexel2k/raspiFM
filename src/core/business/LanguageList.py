from __future__ import annotations
from datetime import datetime

class LanguageList:
    __slots__ = ["__lastupdate", "__languagelist"]
    __lastupdate:datetime

    #Key is name, value is code, as code can be None for exotic languages and dialects
    __languagelist:dict

    @property
    def lastupdate(self) -> datetime:
        return self.__lastupdate
    
    @property
    def languagelist(self) -> dict:
        return self.__languagelist

    @classmethod
    def from_default(cls, languagelist:dict) -> LanguageList:
        if(not languagelist):
            raise ValueError("languagelist must not be null for LanguageList.")
        
        obj = cls()

        obj.__setattr__(f"_LanguageList__lastupdate", datetime.now())
        obj.__setattr__(f"_LanguageList__languagelist", languagelist)

        return obj

    @classmethod
    def deserialize(cls, serializationdata:dict) -> LanguageList:
        if (not serializationdata):
            raise TypeError("Argument serializationdata must be given for LanguageList deserialization.")

        obj = cls()

        for slot in cls.__slots__:
            dictkey = slot[2:]
            if(not(dictkey in serializationdata)):
                raise TypeError(f"{dictkey} key not found in LanguageList serialization data.")

            obj.__setattr__(f"_LanguageList{slot}", serializationdata[dictkey])

        return obj





