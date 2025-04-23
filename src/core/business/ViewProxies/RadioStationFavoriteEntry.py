from core.business.RadioStation import RadioStation

class RadioStationFavoriteEntry:
    __slots__ = ["__radiostation", "__displayorder"]
    __radiostation:RadioStation
    __displayorder:int

    @property
    def radiostation(self) -> RadioStation:
        return self.__radiostation
    
    @property
    def displayorder(self) -> int:
        return self.__displayorder
    
    @displayorder.setter
    def displayorder(self, value:int) -> None:
        self.__displayorder = value

    def __init__(self, radiostation:RadioStation, displayorder:int):
        self.__radiostation = radiostation
        self.__displayorder = displayorder

    def to_dict(self) -> dict:
        return {"radiostation":self.__radiostation.to_dict(),
                "displayorder":self.__displayorder
                }  