from __future__ import annotations
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

    @classmethod
    def from_default(cls, tags:list) -> TagList:
        if(not tags):
            raise ValueError("tags must not be null for TagList.")
        
        obj = cls()

        obj.__setattr__(f"_TagList__lastupdate", datetime.now())
        tagsinternal = list(tags)
        tagsinternal.sort()
        obj.__setattr__(f"_TagList__taglist", tagsinternal)

        return obj

    @classmethod
    def deserialize(cls, serializationdata:dict) -> TagList:
        if (not serializationdata):
            raise TypeError("Argument serializationdata must be given for TagList deserialization.")

        obj = cls()

        for slot in cls.__slots__:
            dictkey = slot[2:]
            if(not(dictkey in serializationdata)):
                raise TypeError(f"{dictkey} key not found in TagList serialization data.")

            obj.__setattr__(f"_TagList{slot}", serializationdata[dictkey])

        return obj

    def filter(self, filter:str) -> None: 
        self.__taglist = [tag for tag in self.__taglist if filter in tag]




