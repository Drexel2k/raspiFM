from datetime import datetime

class TagList:
    __slots__ = ["__lastupdate", "__taglist"]
    __lastupdate:datetime
    __taglist:list

    @property
    def lastupdate(self):
        return self.__lastupdate
    
    @property
    def taglist(self):
        return self.__taglist

    def __init__(self, tags:list, lastupdate:datetime=datetime.now()):
        self.__lastupdate = lastupdate
        self.__taglist = tags
        self.__taglist.sort()




