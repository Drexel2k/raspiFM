from __future__ import annotations
from uuid import UUID

class RadioStation:
    __slots__ = ["__uuid", "__name", "__url", "__countrycode", "__languagecodes", "__homepage", "__faviconb64", "__faviconextension", "__codec", "__bitrate", "__tags"]
    __uuid:UUID
    __name:str
    __url:str
    __languagecodes:str
    __homepage:str
    __faviconb64:str
    __faviconextension:str
    __countrycode:str
    __codec:str
    __bitrate:int
    __tags:list

    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def uuid(self) -> UUID:
        return self.__uuid
    
    @property
    def url(self) -> str:
        return self.__url
    
    @property
    def countrycode(self) -> str:
        return self.__countrycode
    
    @property
    def languacecodes(self) -> str:
        return self.__languagecodes
    
    @property
    def homepage(self) -> str:
        return self.__homepage
    
    @property
    def faviconb64(self) -> str:
        return self.__faviconb64

    @property
    def faviconextension(self) -> str:
        return self.__faviconextension
    
    @property
    def codec(self) -> str:
        return self.__codec
    
    @property
    def bitrate(self) -> int:
        return self.__bitrate
    
    @property
    def tags(self) -> list:
        return self.__tags

    @classmethod
    def from_default(cls, uuid:str, name:str, url:str, codec:str, countrycode:str=None, languagecodes:str=None, homepage:str=None, faviconb64:str=None, faviconextension:str=None, bitrate:int=None, tags:list=None) -> RadioStation:
        if(not uuid or not name or not url or not codec):
            raise ValueError("uuid, name or url must not be null for RadioStation.")
        
        obj = cls()

        obj.__setattr__(f"_RadioStation__uuid", UUID(uuid))
        obj.__setattr__(f"_RadioStation__name", name)
        obj.__setattr__(f"_RadioStation__url", url)
        obj.__setattr__(f"_RadioStation__codec", codec)
        obj.__setattr__(f"_RadioStation__countrycode", countrycode)
        obj.__setattr__(f"_RadioStation__languagecodes", languagecodes)
        obj.__setattr__(f"_RadioStation__homepage", homepage)
        obj.__setattr__(f"_RadioStation__faviconb64", faviconb64)
        obj.__setattr__(f"_RadioStation__faviconextension", faviconextension)
        obj.__setattr__(f"_RadioStation__bitrate", bitrate)
        obj.__setattr__(f"_RadioStation__tags", tags)

        return obj

    @classmethod
    def deserialize(cls, serializationdata:dict) -> RadioStation:
        if (not serializationdata):
            raise TypeError("Argument serializationdata must be given for RadioStation deserialization.")

        obj = cls()

        for slot in cls.__slots__:
            dictkey = slot[2:]
            if(not(dictkey in serializationdata)):
                raise TypeError(f"{dictkey} key not found in RadioStation serialization data.")

            obj.__setattr__(f"_RadioStation{slot}", serializationdata[dictkey])

        return obj
