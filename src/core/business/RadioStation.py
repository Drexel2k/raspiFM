class RadioStation:
    __slots__ = ["__uuid", "__name", "__url", "__languagecodes", "__homepage"]
    __uuid:str
    __name:str
    __url:str
    __languagecodes:str
    __homepage:str

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

    def __init__(self, uuid:str, name:str, url:str, languagecodes:str, homepage:str):
        self.__uuid = uuid
        self.__name = name
        self.__url = url
        self.__languagecodes = languagecodes
        self.__homepage = homepage

