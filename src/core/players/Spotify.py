from __future__ import annotations

from core.players.SpotifyInfo import SpotifyInfo
from core.players.PlayerState import PlayerState
from core.business.RadioStation import RadioStation

class Spotify:
    __slots__ = ["__state", "__spotifyinfo"]
    __instance:Spotify = None
    __state:PlayerState
    __spotifyinfo:SpotifyInfo

    @property
    def isplaying(self) -> bool:
        return self.__state == PlayerState.Playing
    
    @isplaying.setter
    def isplaying(self, value: bool) -> None:
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
    def currentlyplaying(self, value: SpotifyInfo) -> None:
        self.__spotifyinfo = value

    def __new__(cls, info:SpotifyInfo = None):
        if cls.__instance is None:
            cls.__instance = super(Spotify, cls).__new__(cls)
            cls.__instance.__init(info)

        return cls.__instance
    
    def __init(self, info:SpotifyInfo):
        if(info == None):
            self.__state = PlayerState.Stopped
        else:
            self.__state = PlayerState.Playing
            self.__spotifyinfo = info

    def stop(self) -> None:
        self.__state = PlayerState.Stopped