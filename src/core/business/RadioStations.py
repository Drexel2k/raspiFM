from uuid import UUID

from .RadioStation import RadioStation

class RadioStations:
    __slots__ = ["__stationlist"]
    __stationlist:list
    
    @property
    def stationlist(self) -> tuple:
        #ensure only Favorites class can edit the list
        return tuple(self.__stationlist)

    def __init__(self, serializationdata:dict=None):
        if(serializationdata):
            for slot in enumerate(self.__slots__):
                dictkey = slot[1][2:]
                if(not(dictkey in serializationdata)):
                    raise TypeError(f"{dictkey} key not found in RadioStations serialization data.")
                
                self.__setattr__(f"_RadioStations{slot[1]}", serializationdata[dictkey])
        else:
            self.__stationlist = []

    def get_station(self, stationuuid:UUID) -> RadioStation:
        return next((station for station in self.__stationlist if station.uuid == stationuuid), None)
    
    def add_station(self, station:RadioStation) -> None:
        if(not station in self.__stationlist):
            self.__stationlist.append(station)

    def remove_station(self, station:RadioStation) -> None:
        if(station in self.__stationlist):
            self.__stationlist.remove(station)