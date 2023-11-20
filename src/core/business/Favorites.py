from uuid import UUID

from .RadioStation import RadioStation
from .FavoriteList import FavoriteList

class Favorites:
    __slots__ = ["__favoritelists"]
    __favoritelists:list
    
    @property
    def favoritelists(self) -> tuple:
        #ensure only Favorites class can edit the list
        return tuple(self.__favoritelists)

    def __init__(self, serializationdata:list=None):
        if(serializationdata):
            for slot in enumerate(self.__slots__):
                dictkey = slot[1][2:]
                if(not(dictkey in serializationdata)):
                    raise TypeError(f"{dictkey} key not found in RadioStation serialization data.")
                
                self.__setattr__(f"_Favorites{slot[1]}", serializationdata[dictkey])
        else:
            self.__favoritelists = [FavoriteList("Default")]
            self.__favoritelists[0].isdefault = True

    def getdefault(self) -> FavoriteList:
        return next(favlist for favlist in self.__favoritelists if favlist.isdefault)
    
    def getlist(self, listuuid:UUID) -> FavoriteList:
        return next((favlist for favlist in self.__favoritelists if favlist.uuid == listuuid), None)