from __future__ import annotations

from . import SpotifyInfo
from .PlayerState import PlayerState
from ...core.business.RadioStation import RadioStation

class Spotify:
    __slots__ = ["__state", "__volume", "__spotifyinfo"]
    __instance:Vlc = None
    __state:PlayerState
    __volume:int
    __spotifyinfo:SpotifyInfo

    @property
    def isplaying(self) -> bool:
        return self.__state == PlayerState.Playing
    
    @isplaying.setter
    def isplaying(self, value) -> None:
        if(value):
            self.__state = PlayerState.Playing
        else:
            self.__state = PlayerState.Stopped
    
    @property
    def currentlyplaying(self) -> SpotifyInfo:
        if(self.__state == PlayerState.Playing):
            return self.__spotifyinfo
        else:
            return None
        
    @currentlyplaying.setter
    def currentlyplaying(self, value) -> None:
        self.__spotifyinfo = value
    
    @property
    def currentvolum(self) -> int:
        return self.__volume

    def __new__(cls, info:SpotifyInfo = None):
        if cls.__instance is None:
            cls.__instance = super(Spotify, cls).__new__(cls)
            cls.__instance.__init(info)

        return cls.__instance
    
    def __init(self, info:SpotifyInfo):
        self.__volume = 50

        if(info == None):
            self.__state = PlayerState.Stopped
        else:
            self.__state = PlayerState.Playing
            self.__spotifyinfo = info

    def stop(self) -> None:
        self.__state = PlayerState.Stopped
    
    def setvolume(self, volume:int) -> None:
        if(volume < 0):
            volume = 0

        if(volume > 100):
            volume = 100

        self.__volume = volume