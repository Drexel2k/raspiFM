from __future__ import annotations
from enum import Enum

import vlc
from vlc import MediaPlayer

class Vlc:
    __slots__ = ["__vlcinstance", "__vlcplayer", "__vlcmedia", "__state"]
    __instance:Vlc = None
    __vlcinstance:vlc.Instance
    __vlcplayer: MediaPlayer
    __vlcmedia:vlc.Media
    __state:PlayerState

    @property
    def isplaying(self) -> bool:
        return self.__state == PlayerState.Playing

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Vlc, cls).__new__(cls)
            cls.__instance.__init()
        return cls.__instance
    
    def __init(self):
        self.__vlcinstance = vlc.Instance()
        self.__vlcplayer = None
        self.__vlcmedia = None
        self.__state = PlayerState.Stopped

    def play(self, url:str, volume) -> None:
        self.__state = PlayerState.Playing
        self.__vlcplayer = self.__vlcinstance.media_player_new()
        self.__vlcmedia = self.__vlcinstance.media_new(url)
        self.__vlcplayer.set_media(self.__vlcmedia)
        self.setvolume(volume)
        self.__vlcplayer.play()

    def stop(self) -> None:
        self.__state = PlayerState.Stopped
        self.__vlcplayer.stop()
        vlc.libvlc_media_player_release(self.__vlcplayer)
        vlc.libvlc_media_release(self.__vlcmedia)

    def getmeta(self) -> str:     
        if(self.isplaying):
            return self.__vlcmedia.get_meta(vlc.Meta.NowPlaying) # vlc.Meta 12: 'NowPlaying', see vlc.py class Meta(_Enum)
    
    def setvolume(self, volume:int) -> None:
        if(volume < 0):
            volume = 0

        if(volume > 100):
            volume = 100

        self.__vlcplayer.audio_set_volume(volume)

    def shutdown(self) -> None:
        if(self.__state == PlayerState.Playing):
            self.stop()

        vlc.libvlc_release(self.__vlcinstance)
        

class PlayerState(Enum):
    Playing = 1
    Stopped = 2