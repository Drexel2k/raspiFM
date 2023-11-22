from ...core.business.FavoriteList import FavoriteList

class FavoriteListView:
    __slots__ = ["__favoritelist"]
    __favoritelist:FavoriteList

    @property
    def favoritelist(self) -> FavoriteList:
        return self.__favoritelist
    
    @property
    def name(self) -> str:
        if(self.__favoritelist.name):
            return self.__favoritelist.name
        else:
            return "{no name}"

    def __init__(self, favoritelist:FavoriteList):
        self.__favoritelist = favoritelist
