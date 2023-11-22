from uuid import UUID

from .FavoriteList import FavoriteList
from ..business.Exceptions import InvalidOperationException

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

    def add_favoritelist(self) -> FavoriteList:
        favoritelist = FavoriteList()
        self.__favoritelists.append(favoritelist)
        return favoritelist
    
    def delete_favoritelist(self, favoritelist:FavoriteList) -> None:
        if(len(self.__favoritelists) <= 1):
            raise InvalidOperationException("Cannot remove last favorite list.")       
        self.__favoritelists.remove(favoritelist)

    def getdefault(self) -> FavoriteList:
        return next(favlist for favlist in self.__favoritelists if favlist.isdefault)
    
    def getlist(self, listuuid:UUID) -> FavoriteList:
        return next((favlist for favlist in self.__favoritelists if favlist.uuid == listuuid), None)