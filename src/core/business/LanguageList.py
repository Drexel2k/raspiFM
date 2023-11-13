from datetime import datetime

class LanguageList:
    __slots__ = ["__lastupdate", "__languagelist"]
    __lastupdate:datetime
    __languagelist:dict

    @property
    def lastupdate(self):
        return self.__lastupdate
    
    @property
    def languagelist(self):
        return self.__languagelist

    def __init__(self, languagelist:dict, lastupdate:datetime=datetime.now()):
        self.__lastupdate = lastupdate
        self.__languagelist = languagelist




