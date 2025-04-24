class SpotifyInfo:
    __slots__ = ["__title", "__album", "__artists", "__arturl"]
    __title:str
    __album:str
    __artists:str
    __arturl:str

    @property
    def title(self) -> str:
        return self.__title
    
    @property
    def album(self) -> str:
        return self.__album
    
    @property
    def artists(self) -> str:
        return self.__artists
    
    @property
    def arturl(self) -> str:
        return self.__arturl

    def __init__(self, title:str, album:str, artists:list, arturl:str):
        self.__title = title
        self.__album = album

        self.__artists = ""
        if not artists is None and len(artists) > 0:
            self.__artists = ", ".join(artists)

        self.__arturl = arturl

    def to_dict(self) -> dict:
        return {"title":self.__title,
                "album":self.__album,
                "artists":self.artists,
                "arturl":self.__arturl
                }