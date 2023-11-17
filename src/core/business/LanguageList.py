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

    def __init__(self, languagelist:dict, lastupdate:datetime=datetime.now()):
        self.__lastupdate = lastupdate
        self.__languagelist = dict(sorted(languagelist.items()))





