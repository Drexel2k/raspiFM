from .FavoriteList import FavoriteList

class Favorites:
    __slots__ = ["__favoriteLists"]
    __favoriteLists:list
    
    @property
    def favoritelists(self) -> tuple:
        #ensure only Favorites class can edit the list
        return tuple(self.__favoriteLists)

    def __init__(self):
        self.__favoriteLists = [FavoriteList("Default")]
        self.__favoriteLists[0].isdefault = True

    def getdefault(self) -> FavoriteList:
        return next(fav for fav in self.__favoriteLists if fav.isdefault)
        




