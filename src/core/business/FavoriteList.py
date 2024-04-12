from __future__ import annotations
from uuid import UUID, uuid4

from core.business.RadioStation import RadioStation

class FavoriteList:
    __slots__ = ["__uuid", "__name", "__isdefault", "__stations", "__displayorder"]
    __uuid:UUID
    __name:str
    __isdefault:bool
    __stations:list
    __displayorder:int

    @property
    def uuid(self) -> UUID:
        return self.__uuid
    
    @property
    def name(self) -> str:
        return self.__name
    
    @name.setter
    def name(self, value: str) -> None:
        self.__name = value
    
    @property
    def isdefault(self) -> bool:
        return self.__isdefault
    
    @isdefault.setter
    def isdefault(self, value:bool) -> None:
        self.__isdefault = value

    @property
    def stations(self) -> tuple:
        #ensure only FavoriteList class can edit the list
        return tuple(self.__stations)
    
    @property
    def displayorder(self) -> bool:
        return self.__displayorder
    
    @displayorder.setter
    def displayorder(self, value:str) -> None:
        self.__displayorder = value

    @classmethod
    def from_default(cls, name:str=None, displayorder:int=0) -> FavoriteList:
        obj = cls()

        obj.__setattr__(f"_FavoriteList__uuid", uuid4())
        obj.__setattr__(f"_FavoriteList__name", name)
        obj.__setattr__(f"_FavoriteList__isdefault", False)
        obj.__setattr__(f"_FavoriteList__stations", [])
        obj.__setattr__(f"_FavoriteList__displayorder", displayorder)

        return obj

    @classmethod
    def deserialize(cls, serializationdata:dict) -> FavoriteList:
        if serializationdata is None:
            raise TypeError("Argument serializationdata must be given for FavoriteList deserialization.")

        obj = cls()

        for slot in cls.__slots__:
            dictkey = slot[2:]
            if not dictkey in serializationdata:
                raise TypeError(f"{dictkey} key not found in FavoriteList serialization data.")

            obj.__setattr__(f"_FavoriteList{slot}", serializationdata[dictkey])

        return obj

    def addstation(self, station:RadioStation) -> None:
        if not station in self.__stations:
            self.__stations.append(station)

    def removestation(self, station:RadioStation) -> None:
        if station in self.__stations:
            self.__stations.remove(station)

    def contains(self, stationuuid:UUID) -> bool:
        return any(station.uuid == stationuuid for station in self.__stations)
            




