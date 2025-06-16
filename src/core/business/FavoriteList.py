from __future__ import annotations
from uuid import UUID, uuid4

from core.business.Direction import Direction
from core.business.InvalidOperationError import InvalidOperationError
from core.business.RadioStation import RadioStation
from core.business.ViewProxies.RadioStationFavoriteEntry import RadioStationFavoriteEntry

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

        obj.__setattr__("_FavoriteList__uuid", uuid4())
        obj.__setattr__("_FavoriteList__name", name)
        obj.__setattr__("_FavoriteList__isdefault", False)
        obj.__setattr__("_FavoriteList__stations", [])
        obj.__setattr__("_FavoriteList__displayorder", displayorder)

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

    def add_station(self, station:RadioStation) -> None:
        found = False
        for stationentry in self.__stations:
            if stationentry.radiostation == station:
                found = True
                break

        if not found:
            displayorder = 0
            if len(self.__stations) > 0:
                displayorder=max(self.__stations, key=lambda stationinternal: stationinternal.displayorder).displayorder + 1

            self.__stations.append(RadioStationFavoriteEntry(station, displayorder))

    def remove_station(self, station:RadioStation) -> None:
        station_index = next((index for index, stationinternal in enumerate(self.__stations) if stationinternal.radiostation  == station), -1)
        if station_index >= 0:
            self.__stations.pop(station_index)

    def contains(self, stationuuid:UUID) -> bool:
        return any(stationinternal.uuid == stationuuid for stationinternal in self.__stations)
    
    def move_station(self, stationuuid:UUID, direction:Direction) -> None:
        radiostation = next((stationinternal for stationinternal in self.__stations if stationinternal.radiostation.uuid == stationuuid), None)
        if not radiostation is None:
            ordered_stations = sorted(self.__stations, key=lambda stationinternal: stationinternal.displayorder)
            currentindex = ordered_stations.index(radiostation)

            if (currentindex <= 0 and direction == Direction.Up) or (currentindex >= len(ordered_stations) - 1 and direction == Direction.Down):
                raise InvalidOperationError(100, "Cannot move first station up oder last station down.")

            ordered_stations.pop(currentindex)

            newindex = 0
            if direction == Direction.Up:
                newindex = currentindex - 1
            else:
                newindex = currentindex + 1

            if newindex < 0:
                newindex = 0

            if newindex > len(ordered_stations) -1:
                ordered_stations.append(radiostation)
            else:
                ordered_stations.insert(newindex, radiostation)

            position = 0
            for station_inorder in ordered_stations:
                station_inorder.displayorder = position
                position += 1
            
    def to_dict(self) -> dict:
        return {"uuid":str(self.__uuid),
                "name":self.__name,
                "isdefault":self.__isdefault,
                "stations":[stationentry.to_dict() for stationentry in self.__stations],
                "displayorder":self.__displayorder
                }  


