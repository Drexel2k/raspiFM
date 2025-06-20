from __future__ import annotations

import vlc
from vlc import MediaPlayer

from core.players.PlayerState import PlayerState
from core.business.RadioStation import RadioStation

class Vlc:
    __slots__ = ["__vlcinstance", "__vlcplayer", "__vlcmedia", "__state", "__volume", "__station"]
    __instance:Vlc = None
    __vlcinstance:vlc.Instance
    __vlcplayer: MediaPlayer
    __vlcmedia:vlc.Media
    __state:PlayerState
    __volume:int
    __station:RadioStation

    @property
    def isplaying(self) -> bool:
        return self.__state == PlayerState.Playing
    
    @property
    def volume(self) -> int:
        return self.__volume

    @volume.setter
    def volume(self, value: int) -> None:
        if value < 0:
            value = 0

        if value > 100:
            value = 100

        self.__volume = value

        if not self.__vlcplayer is None:
            self.__vlcplayer.audio_set_volume(self.__volume)
    
    @property
    def currentstation(self) -> RadioStation:
        return self.__station

    @currentstation.setter
    def currentstation(self, value: RadioStation) -> None:
        self.__station = value

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Vlc, cls).__new__(cls)
            cls.__instance.__init()

        return cls.__instance
    
    def __init(self):
        self.__vlcinstance = vlc.Instance()
        self.__vlcplayer = None
        self.__vlcmedia = None
        self.__station = None
        self.__volume = 50
        self.__state = PlayerState.Stopped

    def play(self, station:RadioStation = None) -> None:
        if station is None and not self.__station:
            raise ValueError("No station to play.")

        if not station is None:
            self.__station = station 

        if self.__state == PlayerState.Playing:
            self.stop()

        self.__state = PlayerState.Playing
        self.__vlcplayer = self.__vlcinstance.media_player_new()
        self.__vlcmedia = self.__vlcinstance.media_new(self.__station.url)
        self.__vlcplayer.set_media(self.__vlcmedia)
        self.__vlcplayer.audio_set_volume(self.__volume)
        self.__vlcplayer.play()

    def stop(self) -> None:
        if self.__state != PlayerState.Stopped:
            self.__state = PlayerState.Stopped
            if not self.__vlcplayer is None:
                self.__vlcplayer.stop()

                vlc.libvlc_media_player_release(self.__vlcplayer)
                self.__vlcplayer = None

                vlc.libvlc_media_release(self.__vlcmedia)
                self.__vlcmedia = None


    def getmeta(self) -> str:     
        if self.isplaying:
            #print(f"Actors: {self.__vlcmedia.get_meta(vlc.Meta.Actors)}")
            #print(f"Album: {self.__vlcmedia.get_meta(vlc.Meta.Album)}")
            #print(f"AlbumArtist: {self.__vlcmedia.get_meta(vlc.Meta.AlbumArtist)}")
            #print(f"Artist: {self.__vlcmedia.get_meta(vlc.Meta.Artist)}")
            #print(f"ArtworkURL: {self.__vlcmedia.get_meta(vlc.Meta.ArtworkURL)}")
            #print(f"Copyright: {self.__vlcmedia.get_meta(vlc.Meta.Copyright)}")
            #print(f"Date: {self.__vlcmedia.get_meta(vlc.Meta.Date)}")
            #print(f"Description: {self.__vlcmedia.get_meta(vlc.Meta.Description)}")
            #print(f"Director: {self.__vlcmedia.get_meta(vlc.Meta.Director)}")
            #print(f"DiscNumber: {self.__vlcmedia.get_meta(vlc.Meta.DiscNumber)}")
            #print(f"DiscTotal: {self.__vlcmedia.get_meta(vlc.Meta.DiscTotal)}")
            #print(f"EncodedBy: {self.__vlcmedia.get_meta(vlc.Meta.EncodedBy)}")
            #print(f"Episode: {self.__vlcmedia.get_meta(vlc.Meta.Episode)}")
            #print(f"Genre: {self.__vlcmedia.get_meta(vlc.Meta.Genre)}")
            #print(f"Language: {self.__vlcmedia.get_meta(vlc.Meta.Language)}")
            #print(f"NowPlaying: {self.__vlcmedia.get_meta(vlc.Meta.NowPlaying)}")
            #print(f"Publisher: {self.__vlcmedia.get_meta(vlc.Meta.Publisher)}")
            #print(f"Rating: {self.__vlcmedia.get_meta(vlc.Meta.Rating)}")
            #print(f"Season: {self.__vlcmedia.get_meta(vlc.Meta.Season)}")
            #print(f"Setting: {self.__vlcmedia.get_meta(vlc.Meta.Setting)}")
            #print(f"ShowName: {self.__vlcmedia.get_meta(vlc.Meta.ShowName)}")
            #print(f"Title: {self.__vlcmedia.get_meta(vlc.Meta.Title)}")
            #print(f"TrackID: {self.__vlcmedia.get_meta(vlc.Meta.TrackID)}")
            #print(f"TrackNumber: {self.__vlcmedia.get_meta(vlc.Meta.TrackNumber)}")
            #print(f"TrackTotal: {self.__vlcmedia.get_meta(vlc.Meta.TrackTotal)}")
            #print(f"URL: {self.__vlcmedia.get_meta(vlc.Meta.URL)}")
            #print(datetime.now())
            return self.__vlcmedia.get_meta(vlc.Meta.NowPlaying)

    def shutdown(self) -> None:
        if self.__state == PlayerState.Playing:
            self.stop()

        vlc.libvlc_release(self.__vlcinstance)
        self.__vlcinstance = None