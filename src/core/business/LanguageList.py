from datetime import datetime

class LanguageList:
    __slots__ = ["__lastupdate", "__languagelist"]
    __lastupdate:datetime
    __languagelist:dict

    @property
    def lastupdate(self) -> datetime:
        return self.__lastupdate
    
    @property
    def languagelist(self) -> dict:
        return self.__languagelist

    def __init__(self, languagelist:dict=None, serializationdata:dict=None):
        if(serializationdata):
            self.__languagelist = {}
            for slot in enumerate(self.__slots__):
                dictkey = slot[1][2:]
                if(not(dictkey in serializationdata)):
                    raise TypeError(f"{dictkey} key not found in LanguageList serialization data.")
                
                self.__setattr__(f"_LanguageList{slot[1]}", serializationdata[dictkey])
        else:
            if(not languagelist):
                raise ValueError("languagelist must not be null for LanguageList.")

            self.__lastupdate = datetime.now()
            self.__languagelist = dict(sorted(languagelist.items()))





