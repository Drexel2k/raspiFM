from __future__ import annotations
from uuid import UUID

from core.business.RadioStation import RadioStation

class RadioStations:
    __slots__ = ["__stationlist"]
    __stationlist:list
    
    @property
    def stationlist(self) -> tuple:
        #ensure only Favorites class can edit the list
        return tuple(self.__stationlist)

    @classmethod
    def from_default(cls) -> RadioStations:        
        obj = cls()

        obj.__setattr__(f"_RadioStations__stationlist", [])

        return obj

    @classmethod
    def deserialize(cls, serializationdata:dict) -> RadioStations:
        if serializationdata is None:
            raise TypeError("Argument serializationdata must be given for RadioStations deserialization.")

        obj = cls()

        for slot in cls.__slots__:
            dictkey = slot[2:]
            if not dictkey in serializationdata:
                raise TypeError(f"{dictkey} key not found in RadioStations serialization data.")

            obj.__setattr__(f"_RadioStations{slot}", serializationdata[dictkey])

        return obj

    def get_station(self, stationuuid:UUID) -> RadioStation:
        return next((station for station in self.__stationlist if station.uuid == stationuuid), None)
    
    def add_station(self, station:RadioStation) -> None:
        if not any(currentstation.uuid == station.uuid for currentstation in self.__stationlist):
            self.__stationlist.append(station)

    def remove_station(self, station:RadioStation) -> None:
        if station in self.__stationlist:
            self.__stationlist.remove(station)