import ctypes
import os
import sys

class UserSettings:
    __slots__ = ["__web_defaultlanguage", "__web_defaultcountry"]

    __web_defaultlanguage:str
    __web_defaultcountry:str

    @property
    def web_defaultlanguage(self) -> str:
        return self.__web_defaultlanguage
    
    @property
    def web_defaultcountry(self) -> str:
        return self.__web_defaultcountry

    def __init__(self, serializationdata = None):
        if(serializationdata):
            for slot in enumerate(self.__slots__):
                dictkey = slot[1][2:]
                if(not(dictkey in serializationdata)):
                    raise TypeError(f"{dictkey} key not found in UserSettings serialization data.")

                self.__setattr__(f"_UserSettings{slot[1]}", serializationdata[dictkey])
        else:
            self.__web_defaultlanguage="german"
            self.__web_defaultcountry="DE"

class Settings:
    __slots__ = ["__serialization_directory", "__usersettings", "__touch_runontouch"]
    __serialization_directory:str
    __touch_runontouch:bool

    __usersettings:UserSettings

    @property
    def serialization_directory(self) -> str:
        return self.__serialization_directory
    
    @property
    def touch_runontouch(self) -> bool:
        return self.__touch_runontouch
    
    @property
    def usersettings(self) -> UserSettings:
        return self.__usersettings
    
    @usersettings.setter
    def name(self, value) -> None:
        self.__usersettings = value

    def __init__(self):
        self.__usersettings = UserSettings()
        self.__touch_runontouch = False  

        self.__serialization_directory = os.path.expanduser('~/raspifm')