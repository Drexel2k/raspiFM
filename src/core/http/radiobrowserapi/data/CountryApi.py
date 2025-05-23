class CountryApi:
    __slots__ = ["__name", "__iso_3166_1", "__stationcount"]
    __name:str
    __iso_3166_1:str
    __stationcount:int
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def iso_3166_1(self) -> str:
        return self.__iso_3166_1
    
    @property
    def stationcount(self) -> int:
        return self.__stationcount

    def __init__(self, apidict:dict):
        for slot in self.__slots__:
            dictkey = slot[2:]
            if not dictkey in apidict:
               raise TypeError(f"{dictkey} key not found in country api response dictionary.")
            self.__setattr__(f"_RadioStationApi{slot}", apidict[dictkey])