from __future__ import annotations
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

    @classmethod
    def from_default(cls) -> Favorites:
        obj = cls()

        favlist = FavoriteList.from_default("Default")
        favlist.isdefault = True
        obj.__setattr__(f"_Favorites__favoritelists", [favlist])

        return obj

    @classmethod
    def deserialize(cls, serializationdata:dict) -> Favorites:
        if (not serializationdata):
            raise TypeError("Argument serializationdata must be given for Favorites deserialization.")

        obj = cls()

        for slot in cls.__slots__:
            dictkey = slot[2:]
            if(not(dictkey in serializationdata)):
                raise TypeError(f"{dictkey} key not found in Favorites serialization data.")

            obj.__setattr__(f"_Favorites{slot}", serializationdata[dictkey])

        return obj

    def add_favoritelist(self) -> FavoriteList:
        favoritelist = FavoriteList.from_default()
        self.__favoritelists.append(favoritelist)
        return favoritelist
    
    def delete_favoritelist(self, listuuid:UUID) -> None:
        if(len(self.__favoritelists) <= 1):
            raise InvalidOperationException("Cannot remove last favorite list.")

        deletelist = self.get_list(listuuid)
        if(deletelist):
            if (deletelist.isdefault):
                newdefaultlist = next(favlist for favlist in self.__favoritelists if favlist != deletelist)
                newdefaultlist.isdefault = True

            self.__favoritelists.remove(deletelist)

    def get_default(self) -> FavoriteList:
        return next(favlist for favlist in self.__favoritelists if favlist.isdefault)
    
    def get_list(self, listuuid:UUID) -> FavoriteList:
        return next((favlist for favlist in self.__favoritelists if favlist.uuid == listuuid), None)
    
    def change_default(self, listuuid:UUID, newdefaultstate:bool) -> None:
        if(newdefaultstate):
            newdefaultlist = self.get_list(listuuid)
            if(newdefaultlist):
                currentdefaultlist = self.get_default()
                currentdefaultlist.isdefault = False
                newdefaultlist.isdefault = True
        else:
            changelist = self.get_list(listuuid)
            currentdefaultlist = self.get_default()
            if(currentdefaultlist == changelist):
                if(len(self.__favoritelists) <= 1):
                    raise InvalidOperationException("Cannot remove default state from last favorite list.")
                
                newdefaultlist = next(favlist for favlist in self.__favoritelists if favlist != currentdefaultlist)
                changelist.isdefault = False
                newdefaultlist.isdefault = True