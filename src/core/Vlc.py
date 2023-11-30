from __future__ import annotations

import vlc
from vlc import MediaPlayer

class Vlc:
    __slots__ = ["__vlcinstance", "__vlcplayer", "__vlcmedia"]
    __instance:Vlc = None
    __vlcinstance:vlc.Instance
    __vlcplayer: MediaPlayer
    __vlcmedia:vlc.Media

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Vlc, cls).__new__(cls)
            cls.__instance.__init()
        return cls.__instance
    
    def __init(self):
        self.__vlcinstance = vlc.Instance()

    def play(self, url:str, volume) -> None:
        self.__vlcplayer = self.__vlcinstance.media_player_new()
        self.__vlcmedia = self.__vlcinstance.media_new(url)
        self.__vlcplayer.set_media(self.__vlcmedia)
        self.setvolume(volume)
        self.__vlcplayer.play()

    def stop(self) -> None:
        self.__vlcplayer.stop()

    def getmeta(self) -> str:     
        if(self.__vlcplayer.is_playing()):
            return self.__vlcmedia.get_meta(vlc.Meta.NowPlaying) # vlc.Meta 12: 'NowPlaying', see vlc.py class Meta(_Enum)
    
    def isplaying(self) -> bool:
        return self.__vlcplayer.is_playing()
    
    def setvolume(self, volume:int) -> None:
        if(volume < 0):
            volume = 0

        if(volume > 100):
            volume = 100

        self.__vlcplayer.audio_set_volume(volume)

