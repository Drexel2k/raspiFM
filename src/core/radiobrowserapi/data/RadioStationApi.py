class RadioStationApi:
    __slots__ = ["__stationuuid", "__name", "__url", "__homepage", "__favicon", "__tags", "__countrycode", "__languagecodes", "__votes", "__codec", "__bitrate", "__clickcount", "__clicktrend"]
    __stationuuid:str
    __name:str
    __url:str
    __homepage:str
    __favicon:str
    __tags:str
    __countrycode:str
    __languagecodes:str
    __votes:int
    __codec:str
    __bitrate:int
    __clickcount:int
    __clicktrend:int

    @property
    def stationuuid(self) -> str:
        return self.__stationuuid
    
    @property
    def name(self):
        return self.__name
    
    @property
    def url(self):
        return self.__url
    
    @property
    def homepage(self):
        return self.__homepage
    
    @property
    def favicon(self):
        return self.__favicon
    
    @property
    def tags(self):
        return self.__tags
    
    @property
    def countrycode(self):
        return self.__countrycode
    
    @property
    def languagecodes(self):
        return self.__languagecodes
    
    @property
    def votes(self):
        return self.__votes
    
    @property
    def codec(self):
        return self.__codec
    
    @property
    def bitrate(self):
        return self.__bitrate
    
    @property
    def clickcount(self):
        return self.__clickcount
    
    @property
    def clicktrend(self):
        return self.__clicktrend

    def __init__(self, apidict:dict):
        for slot in enumerate(self.__slots__):
            dictkey = slot[1][2:]
            if(not(dictkey in apidict)):
               raise TypeError(f"{dictkey} key not found in radio station api response dictionary.")
            self.__setattr__(f"_RadioStationApi{slot[1]}", apidict[dictkey])

