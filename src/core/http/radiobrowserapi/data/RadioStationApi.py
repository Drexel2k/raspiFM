class RadioStationApi:
    __slots__ = ["__stationuuid", "__name", "__url", "__url_resolved", "__homepage", "__favicon", "__tags", "__countrycode", "__languagecodes", "__votes", "__codec", "__bitrate", "__hls", "__clickcount", "__clicktrend"]
    __stationuuid:str
    __name:str
    __url:str
    __url_resolved:str
    __languagecodes:str
    __homepage:str
    __favicon:str
    __tags:list
    __countrycode:str
    __votes:int
    __codec:str
    __bitrate:int
    __hls:bool
    __clickcount:int
    __clicktrend:int

    @property
    def stationuuid(self) -> str:
        return self.__stationuuid
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def url(self) -> str:
        return self.__url
    
    @property
    def url_resolved(self) -> str:
        return self.__url_resolved
    
    @property
    def languagecodes(self) -> str:
        return self.__languagecodes
    
    @property
    def homepage(self) -> str:
        return self.__homepage
    
    @property
    def favicon(self) -> str:
        return self.__favicon
    
    @property
    def tags(self) -> list:
        return self.__tags
    
    @property
    def countrycode(self) -> str:
        return self.__countrycode
    
    @property
    def votes(self) -> int:
        return self.__votes
    
    @property
    def codec(self) -> str:
        return self.__codec
    
    @property
    def bitrate(self) -> int:
        return self.__bitrate
    
    @property
    def hls(self) -> bool:
        return self.__hls
    
    @property
    def clickcount(self) -> int:
        return self.__clickcount
    
    @property
    def clicktrend(self) -> int:
        return self.__clicktrend

    def __init__(self, apidict:dict):
        for slot in self.__slots__:
            dictkey = slot[2:]
            if not dictkey in apidict:
               raise TypeError(f"{dictkey} key not found in radio station api response dictionary.")
            if dictkey != "tags":
                self.__setattr__(f"_RadioStationApi{slot}", apidict[dictkey])
            else:
                self.__setattr__(f"_RadioStationApi{slot}", apidict[dictkey].split(","))

    def to_dict(self) -> dict:
        return {"stationuuid":self.__stationuuid,
                "name":self.__name,
                "url":self.__url,
                "url_resolved":self.__url_resolved,
                "languagecodes":self.__languagecodes,
                "homepage":self.__homepage,
                "favicon":self.__favicon,
                "tags":self.__tags,
                "countrycode":self.__countrycode,
                "votes":self.__votes,
                "codec":self.__codec,
                "bitrate":self.__bitrate,
                "hls":self.__hls,
                "clickcount":self.__clickcount,
                "clicktrend":self.__clicktrend
                }    

