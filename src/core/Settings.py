from __future__ import annotations
import os
from uuid import UUID

from core.LogLevel import LogLevel
from core.StartWith import StartWith

class UserSettings:
    __slots__ = ["__touch_runontouch", "__web_defaultlanguage", "__web_defaultcountry", "__touch_startwith", "__touch_laststation", "__touch_volume", "__all_loglevel"]

    __touch_runontouch:bool
    __web_defaultlanguage:str
    __web_defaultcountry:str
    __touch_startwith:StartWith
    __touch_laststation:UUID
    __touch_volume:int
    __all_loglevel:LogLevel

    @property
    def touch_runontouch(self) -> bool:
        return self.__touch_runontouch

    @property
    def web_defaultlanguage(self) -> str:
        return self.__web_defaultlanguage
    
    @web_defaultlanguage.setter
    def web_defaultlanguage(self, value: str) -> None:
        self.__web_defaultlanguage = value
    
    @property
    def web_defaultcountry(self) -> str:
        return self.__web_defaultcountry
    
    @web_defaultcountry.setter
    def web_defaultcountry(self, value: str) -> None:
        self.__web_defaultcountry = value

    @property
    def touch_startwith(self) -> StartWith:
        return self.__touch_startwith
    
    @touch_startwith.setter
    def touch_startwith(self, value: StartWith) -> None:
        self.__touch_startwith = value

    @property
    def touch_laststation(self) -> UUID:
        return self.__touch_laststation
    
    @touch_laststation.setter
    def touch_laststation(self, value: UUID) -> None:
        self.__touch_laststation = value

    @property
    def touch_volume(self) -> int:
        return self.__touch_volume
    
    @touch_volume.setter
    def touch_volume(self, value: int) -> None:
        self.__touch_volume = value

    @property
    def all_loglevel(self) -> LogLevel:
        return self.__all_loglevel
    
    @all_loglevel.setter
    def all_loglevel(self, value: LogLevel) -> None:
        self.__all_loglevel = value

    @classmethod
    def from_default(cls) -> UserSettings:    
        obj = cls()

        obj.__setattr__(f"_UserSettings__touch_runontouch", True)
        obj.__setattr__(f"_UserSettings__web_defaultlanguage", "german")
        obj.__setattr__(f"_UserSettings__web_defaultcountry", "DE")
        obj.__setattr__(f"_UserSettings__touch_startwith", StartWith.LastStation)
        obj.__setattr__(f"_UserSettings__touch_laststation", None)
        obj.__setattr__(f"_UserSettings__touch_volume", 50)
        obj.__setattr__(f"_UserSettings__all_loglevel", LogLevel.Debug)

        return obj

    @classmethod
    def deserialize(cls, serializationdata:dict) -> UserSettings:
        if serializationdata is None:
            raise TypeError("Argument serializationdata must be given for UserSettings deserialization.")

        obj = cls()

        for slot in cls.__slots__:
            dictkey = slot[2:]
            if not dictkey in serializationdata:
                raise TypeError(f"{dictkey} key not found in UserSettings serialization data.")

            obj.__setattr__(f"_UserSettings{slot}", serializationdata[dictkey])

        return obj

class Settings:
    __slots__ = ["__serialization_directory", "__usersettings"]

    __serialization_directory:str
    __usersettings:UserSettings

    @property
    def serialization_directory(self) -> str:
        return self.__serialization_directory
    
    @property
    def usersettings(self) -> UserSettings:
        return self.__usersettings
    
    @usersettings.setter
    def usersettings(self, value: UserSettings) -> None:
        self.__usersettings = value

    def __init__(self):
        self.__usersettings = None
        self.__serialization_directory = os.path.expanduser('~/raspifm')