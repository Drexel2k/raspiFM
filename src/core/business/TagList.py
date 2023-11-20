from datetime import datetime

class TagList:
    __slots__ = ["__lastupdate", "__taglist"]
    __lastupdate:datetime
    __taglist:list

    @property
    def lastupdate(self) -> datetime:
        return self.__lastupdate
    
    @property
    def taglist(self) -> list:
        return self.__taglist

    def __init__(self, tags:list=None, serializationdata:dict=None):
        if(serializationdata):
            self.__taglist = []
            for slot in enumerate(self.__slots__):
                dictkey = slot[1][2:]
                if(not(dictkey in serializationdata)):
                    raise TypeError(f"{dictkey} key not found in TagList serialization data.")
                
                self.__setattr__(f"_TagList{slot[1]}", serializationdata[dictkey])
        else:
            if(not tags):
                raise ValueError("tags must not be null for TagList.")
            self.__lastupdate = datetime.now()
            self.__taglist = list(tags)
            self.__taglist.sort()

    def filter(self, filter:str) -> None: 
        self.__taglist = [tag for tag in self.__taglist if filter in tag]




