from uuid import UUID

class RadioStation:
    __slots__ = ["__uuid", "__name", "__url", "__languagecodes", "__homepage", "__faviconb64"]
    __uuid:UUID
    __name:str
    __url:str
    __languagecodes:str
    __homepage:str
    __faviconb64:str

    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def uuid(self) -> str:
        return self.__uuid
    
    @property
    def url(self) -> str:
        return self.__url
    
    @property
    def languacecodes(self) -> str:
        return self.__languagecodes
    
    @property
    def homepage(self) -> str:
        return self.__homepage
    
    @property
    def faviconb64(self) -> str:
        return self.__faviconb64

    def __init__(self, uuid:str=None, name:str=None, url:str=None, languagecodes:str=None, homepage:str=None, faviconb64:str=None, serializationdata:dict=None):
        if(serializationdata):
            for slot in enumerate(self.__slots__):
                dictkey = slot[1][2:]
                if(not(dictkey in serializationdata)):
                    raise TypeError(f"{dictkey} key not found in RadioStation serialization data.")

                self.__setattr__(f"_RadioStation{slot[1]}", serializationdata[dictkey])
        else:
            if(not uuid or not name or not url):
                raise ValueError("uuid, name or url must not be null for RadioStation.")
            self.__uuid = UUID(uuid)
            self.__name = name
            self.__url = url
            self.__languagecodes = languagecodes
            self.__homepage = homepage
            self.__faviconb64 = faviconb64

