from core.business.RadioStation import RadioStation

class RadioStationView:
    __slots__ = ["__radiostation", "__isinfavoritelist"]
    __radiostation:RadioStation
    __isinfavoritelist:bool

    @property
    def radiostation(self) -> RadioStation:
        return self.__radiostation
    
    @property
    def isinfavoritelist(self) -> bool:
        return self.__isinfavoritelist

    def __init__(self, radiostation:RadioStation, isinfavoritelist:bool):
        self.__radiostation = radiostation
        self.__isinfavoritelist = isinfavoritelist

