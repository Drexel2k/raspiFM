class FavoriteList:
    __slots__ = ["__name", "__isdefault"]
    __name:str
    __isdefault:bool
    
    @property
    def name(self) -> str:
        return self.__name
    
    @name.setter
    def name(self, value) -> None:
        self.__name = value
    
    @property
    def isdefault(self) -> bool:
        return self.__isdefault
    
    @isdefault.setter
    def isdefault(self, value) -> None:
        self.__isdefault = value

    def __init__(self, name:str):
        self.__name = name
        self.__isdefault = False




