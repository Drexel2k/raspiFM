from __future__ import annotations
from uuid import UUID

from core.business.Direction import Direction
from core.business.FavoriteList import FavoriteList
from core.business.Exceptions import InvalidOperationException

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
        if serializationdata is None:
            raise TypeError("Argument serializationdata must be given for Favorites deserialization.")

        obj = cls()

        for slot in cls.__slots__:
            dictkey = slot[2:]
            if not dictkey in serializationdata:
                raise TypeError(f"{dictkey} key not found in Favorites serialization data.")

            obj.__setattr__(f"_Favorites{slot}", serializationdata[dictkey])

        return obj

    def add_favoritelist(self) -> FavoriteList:
        favoritelist = FavoriteList.from_default(displayorder=max(self.__favoritelists, key=lambda favlistinternal: favlistinternal.displayorder).displayorder + 1)
        self.__favoritelists.append(favoritelist)
        return favoritelist
    
    def delete_favoritelist(self, listuuid:UUID) -> None:
        if len(self.__favoritelists) <= 1:
            raise InvalidOperationException("Cannot remove last favorite list.")

        deletelist = self.get_list(listuuid)
        if not deletelist is None:
            if deletelist.isdefault:
                newdefaultlist = next(favlistinternal for favlistinternal in self.__favoritelists if favlistinternal != deletelist)
                newdefaultlist.isdefault = True

            self.__favoritelists.remove(deletelist)

    def get_default(self) -> FavoriteList:
        return next(favlistinternal for favlistinternal in self.__favoritelists if favlistinternal.isdefault)
    
    def get_list(self, listuuid:UUID) -> FavoriteList:
        return next((favlistinternal for favlistinternal in self.__favoritelists if favlistinternal.uuid == listuuid), None)
    
    def change_default(self, listuuid:UUID, newdefaultstate:bool) -> None:
        if newdefaultstate:
            newdefaultlist = self.get_list(listuuid)
            if not newdefaultlist is None:
                currentdefaultlist = self.get_default()
                currentdefaultlist.isdefault = False
                newdefaultlist.isdefault = True
        else:
            changelist = self.get_list(listuuid)
            currentdefaultlist = self.get_default()
            if currentdefaultlist == changelist:
                if len(self.__favoritelists) <= 1:
                    raise InvalidOperationException("Cannot remove default state from last favorite list.")
                
                newdefaultlist = next(favlistinternal for favlistinternal in self.__favoritelists if favlistinternal != currentdefaultlist)
                changelist.isdefault = False
                newdefaultlist.isdefault = True

    def move_list(self, listuuid:UUID, direction:Direction) -> None:
        favoritelist = self.get_list(listuuid)
        if not favoritelist is None:
            ordered_favoritelists = sorted(self.__favoritelists, key=lambda favoritelistinternal: favoritelistinternal.displayorder)
            currentindex = ordered_favoritelists.index(favoritelist)

            if (currentindex <= 0 and direction == Direction.Up) or (currentindex >= len(ordered_favoritelists) - 1 and direction == Direction.Down):
                raise InvalidOperationException("Cannot move first favorite list up oder last favorite list down.")

            ordered_favoritelists.pop(currentindex)

            newindex = 0
            if direction == Direction.Up:
                newindex = currentindex - 1
            else:
                newindex = currentindex + 1

            if newindex < 0:
                newindex = 0

            if newindex > len(ordered_favoritelists) -1:
                ordered_favoritelists.append(favoritelist)
            else:
                ordered_favoritelists.insert(newindex, favoritelist)

            position = 0
            for favoritelist_inorder in ordered_favoritelists:
                favoritelist_inorder.displayorder = position
                position += 1

    def move_station_in_list(self, favlistuuid:UUID, stationuuid:UUID, direction:Direction) -> None:
        favlist =   self.get_list(favlistuuid)
        if not favlist is None:
            favlist.move_station(stationuuid, direction)