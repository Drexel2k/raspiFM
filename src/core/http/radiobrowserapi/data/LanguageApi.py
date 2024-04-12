class LanguageApi:
    __slots__ = ["__name", "__iso_639", "__stationcount"]
    __name:str
    __iso_639:str
    __stationcount:int
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def iso_639(self) -> str:
        return self.__iso_639
    
    @property
    def stationcount(self) -> int:
        return self.__stationcount

    def __init__(self, apidict:dict):
        for slot in enumerate(self.__slots__):
            dictkey = slot[1][2:]
            if not dictkey in apidict:
               raise TypeError(f"{dictkey} key not found in country api response dictionary.")
            self.__setattr__(f"_RadioStationApi{slot[1]}", apidict[dictkey])

