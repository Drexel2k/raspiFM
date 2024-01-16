from uuid import UUID, uuid4

from .RadioStation import RadioStation

class FavoriteList:
    __slots__ = ["__uuid", "__name", "__isdefault", "__stations"]
    __uuid:UUID
    __name:str
    __isdefault:bool
    __stations:[]

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
    def isdefault(self, value : bool) -> None:
        self.__isdefault = value

    @property
    def stations(self) -> tuple:
        #ensure only FavoriteList class can edit the list
        return tuple(self.__stations)

    def __init__(self, name:str=None, serializationdata:dict=None):
        self.__stations = []

        if(serializationdata):
            for slot in enumerate(self.__slots__):
                dictkey = slot[1][2:]
                if(not(dictkey in serializationdata)):
                    raise TypeError(f"{dictkey} key not found in FavoriteList serialization data.")

                self.__setattr__(f"_FavoriteList{slot[1]}", serializationdata[dictkey])
        else:
            self.__uuid = uuid4()
            self.__name = name
            self.__isdefault = False

    def addstation(self, station:RadioStation) -> None:
        if(not station in self.__stations):
            self.__stations.append(station)

    def removestation(self, station:RadioStation) -> None:
        if(station in self.__stations):
            self.__stations.remove(station)

    def contains(self, stationuuid:UUID) -> bool:
        return any(station.uuid == stationuuid for station in self.__stations)
            




