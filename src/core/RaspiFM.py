from __future__ import annotations

from collections import deque
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from uuid import UUID
from os import path

from jeepney import DBusAddress, new_method_call, MatchRule, message_bus, HeaderFields
from jeepney.io.blocking import Proxy, DBusConnection
from jeepney.io.common import FilterHandle
from jeepney.io.blocking import open_dbus_connection

from core import dbusstrings
from core.StartWith import StartWith
from core.json.JsonSerializer import JsonSerializer
from core.json.JsonDeserializer import JsonDeserializer
from core.Settings import Settings, UserSettings
from core.http.radiobrowserapi import requestbase
from core.http.radiobrowserapi import stationapi
from core.http.radiobrowserapi.data.RadioStationApi import RadioStationApi
from core.http.radiobrowserapi import listapi
from core.http.basics import httpcontent
from core.business.Direction import Direction
from core.business.CountryList import CountryList
from core.business.LanguageList import LanguageList
from core.business.TagList import TagList
from core.business.Favorites import Favorites
from core.business.RadioStations import RadioStations
from core.business.RadioStation import RadioStation
from core.business.FavoriteList import FavoriteList
from core.players.Spotify import Spotify
from core.players.SpotifyInfo import SpotifyInfo
from core.players.Vlc import Vlc
from common import utils

#todo: maybe split public core interface in several proxy classes
class RaspiFM:
    __slots__ = ["__favorites", "__radiostations", "__settings", "__version", "__spotify_dbusname", "__dbus_spotify_filter", "__dbus_connection", "__dbus_queue", "__dbus_proxy"]
    __instance:RaspiFM = None
    __radiostations:RadioStations
    __favorites:Favorites
    __settings:Settings
    __version:str
    __spotify_dbusname:str
    __dbus_spotify_filter:FilterHandle
    __dbus_connection:DBusConnection
    __dbus_queue:deque
    __dbus_proxy:Proxy

    @property
    def version(self) -> str:
        return self.__version
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(RaspiFM, cls).__new__(cls)
            cls.__instance.__init()
        return cls.__instance
    
    def __init(self):
        self.__version = "1.1.0"
        requestbase.version = self.__version

        self.__settings = Settings()

        if not Path(self.__settings.serialization_directory).is_dir():
            Path(self.__settings.serialization_directory).mkdir(parents=True, exist_ok=True)

        if not Path(self.__settings.serialization_directory, "cache/").is_dir():    
            Path(self.__settings.serialization_directory, "cache/").mkdir(parents=True, exist_ok=True)
            
        JsonSerializer(self.__settings.serialization_directory)
        JsonDeserializer(self.__settings.serialization_directory)

        self.__radiostations = JsonDeserializer().get_radiostations()
        if self.__radiostations is None:
            self.__radiostations = RadioStations.from_default()

        self.__favorites = JsonDeserializer().get_favorites(self.__radiostations)
        if self.__favorites is None:
            self.__favorites = Favorites.from_default()

        usersettings = JsonDeserializer().get_usersettings()
        self.__settings.usersettings = usersettings if usersettings else UserSettings.from_default()

        Vlc().volume = self.__settings.usersettings.touch_volume

        self.__initializespotify()

    def __initializespotify(self) -> None:
        self.__spotify_dbusname = None

        self.__dbus_connection = open_dbus_connection(bus='SYSTEM')
        self.__dbus_proxy = Proxy(message_bus, self.__dbus_connection)
        self.__dbus_queue = deque()

        dbus_address = DBusAddress(dbusstrings.dbuspath, dbusstrings.dbusname, dbusstrings.dbusinterface)
        dbus_list_names_message = new_method_call(dbus_address, 'ListNames')

        dbus_list_names_reply = self.__dbus_connection.send_and_get_reply(dbus_list_names_message)

        #check if spotify is already up
        for dbus_name in dbus_list_names_reply.body[0]:
            if dbus_name.startswith(dbusstrings.spotifydservicestart):
               self.__spotify_dbusname = dbus_name
               break


        dbus_properties_address = DBusAddress(dbusstrings.dbuspath, dbusstrings.dbusname, dbusstrings.dbusinterface)
        #listen for service names entering or leaving the bus
        dbus_changed_match_rule = MatchRule(
            type="signal",
            interface=dbus_properties_address.interface,
            member=dbusstrings.dbussignalnameownerchanged,
            path=dbus_properties_address.object_path
            )

        self.__dbus_proxy.AddMatch(dbus_changed_match_rule)
        self.__dbus_connection.filter(dbus_changed_match_rule, queue=self.__dbus_queue)

        if not utils.str_isnullorwhitespace(self.__spotify_dbusname):
            self.__spotify_service_presence_change(True)

        while True:
            signal_message = self.__dbus_connection.recv_until_filtered(self.__dbus_queue)
            if signal_message.header.fields[HeaderFields.path] == "/org/mpris/MediaPlayer2":
                #spotify state changed
                self.__spotifyd_propertieschanged(signal_message.body[1])

            if signal_message.header.fields[HeaderFields.path] == "/org/freedesktop/DBus":
                servicename = signal_message.body[0]
                newowner = signal_message.body[1]
                oldowner = signal_message.body[2]

                if servicename.startswith("org.mpris.MediaPlayer2.spotifyd.instance"):
                    #service new on the bus
                    if utils.str_isnullorwhitespace(newowner):
                        self.__spotify_dbusname = servicename
                        self.__spotify_service_presence_change(True)
                    #service left bus
                    if utils.str_isnullorwhitespace(oldowner):
                        self.__spotify_dbusname = None
                        self.__spotify_service_presence_change(False)

    def __spotify_service_presence_change(self, spotify_present:bool) -> None:
        if spotify_present:
            dbus_address = DBusAddress(dbusstrings.spotifydpath, self.__spotify_dbusname, dbusstrings.dbuspropertiesinterface)
            dbus_spotify_playbackstatus_message = new_method_call(dbus_address, dbusstrings.dbusmethodget, "ss", (dbusstrings.spotifydinterface, dbusstrings.spotifydpropertyplaybackstatus))

            dbus_spotify_playbackstatus_reply = self.__dbus_connection.send_and_get_reply(dbus_spotify_playbackstatus_message)
            if dbus_spotify_playbackstatus_reply.body[0][1] == "Playing":
                dbus_spotify_playbackstatus_message = new_method_call(dbus_address, dbusstrings.dbusmethodget, "ss", (dbusstrings.spotifydinterface, dbusstrings.spotifydpropertymetadata))
                dbus_spotify_playbackstatus_reply = self.__dbus_connection.send_and_get_reply(dbus_spotify_playbackstatus_message)
                metadata = dbus_spotify_playbackstatus_reply.body[0][1]
                Spotify().currentlyplaying = {"title":metadata[dbusstrings.spotifydmetadatatitle][1],
                                                    "album":metadata[dbusstrings.spotifydmetadataalbum][1],
                                                    "artists":metadata[dbusstrings.spotifydmetadataartists][1],
                                                    "arturl":metadata[dbusstrings.spotifydmetadataarturl][1]}
                
            dbus_spotify_address = DBusAddress(dbusstrings.spotifydpath, self.__spotify_dbusname, dbusstrings.dbuspropertiesinterface)

            dbus_spotify_changed_match_rule = MatchRule(
                    type="signal",
                    interface=dbus_spotify_address.interface,
                    member=dbusstrings.dbussignalpropertieschanged,
                    path=dbus_spotify_address.object_path
                    )
                
            self.__dbus_proxy.AddMatch(dbus_spotify_changed_match_rule)
            self.__dbus_spotify_filter = self.__dbus_connection.filter(dbus_spotify_changed_match_rule, queue=self.__dbus_queue)
        else:
            self.__dbus_spotify_filter.close()
            Spotify().currentlyplaying = None


    def __spotifyd_propertieschanged(self, changeproperties:dict) -> None:
        #Sometimes, not reproducable, not alle infos are in the changeproperties, onyl one attribute like volume is in it.
        #Normaly after that another propertieschange signal comes in with the full infos.
        if not dbusstrings.spotifydpropertymetadata in changeproperties or not dbusstrings.spotifydpropertyplaybackstatus in changeproperties:
            return
            #interface = QtDBus.QDBusInterface(self.__spotify_dbusname, dbusstrings.spotifydpath, dbusstrings.dbuspropertiesinterface, self.__system_dbusconnection)
            #msg = interface.call(dbusstrings.dbusmethodgetall, dbusstrings.spotifydinterface)
            #changeproperties = msg.arguments()[0]

        metadata = changeproperties[dbusstrings.spotifydpropertymetadata][1]
        #todo:maybe notify GUI
        Spotify().currentlyplaying = {"title":metadata[dbusstrings.spotifydmetadatatitle][1], 
                                            "album":metadata[dbusstrings.spotifydmetadataalbum][1],
                                            "artists":metadata[dbusstrings.spotifydmetadataartists][1],
                                            "arturl":metadata[dbusstrings.spotifydmetadataarturl][1]
                                            }
        
        if changeproperties[dbusstrings.spotifydpropertyplaybackstatus][1] == "Playing":
            Vlc().stop()

            #todo:notify GUI

        else:
            if Spotify().isplaying:
                #Not only triggered when Spotify stopped via app, but also when radio
                #was manually started again, so this is no sign of nothing is playing!
                #todo:notify GUI
                self.spotify_set_isplaying(False)

                #todo:notify GUI
    
    def stationapis_get(self, name:str, country:str, language:str, tags:list, orderby:str, reverse:bool, page:int) -> list:
        return list(map(lambda radiostationdict: RadioStationApi(radiostationdict),
                   stationapi.query_stations_advanced(name, country, language, tags, orderby, reverse, page)))
    
    def stations_getstation(self, station_uuid:UUID) -> RadioStation:
        return self.__radiostations.get_station(station_uuid)
    
    def stations_deletestation(self, uuid:UUID, serialize:bool=True) -> None:
        station = self.stations_getstation(uuid)

        deletestation = True
        for favlist in self.__favorites.favoritelists:
            stationresult = next((stationinternal for stationinternal in favlist.stations if stationinternal.radiostation == station), None)
            if not stationresult is None:
                deletestation = False
                break
        
        if uuid == self.__settings.usersettings.touch_laststation:
            deletestation = False

        if deletestation:
            self.__radiostations.remove_station(station)
            if serialize:
                JsonSerializer().serialize_radiostations(self.__radiostations)
    
    def countries_get(self) -> CountryList:
        countrylist = JsonDeserializer().get_countrylist()

        sevendays = timedelta(days=7)
        if countrylist is None or countrylist.lastupdate + sevendays < datetime.now():
            countrylistapi = listapi.query_countrylist()
            countrylist = CountryList.from_default({ countryinternal["name"] : countryinternal["iso_3166_1"] for countryinternal in countrylistapi })
            JsonSerializer().serialize_countrylist(countrylist)

        return countrylist
    
    def languages_get(self) -> LanguageList:
        languagelist = JsonDeserializer().get_languagelist()

        sevendays = timedelta(days=7)
        if languagelist is None or languagelist.lastupdate + sevendays < datetime.now():
            languagelistapi = listapi.query_languagelist()
            languagelist = LanguageList.from_default({ languageinternal["name"] : languageinternal["iso_639"] for languageinternal in languagelistapi })
            JsonSerializer().serialize_languagelist(languagelist)

        return languagelist
    
    def tags_get(self, filter:str=None) -> TagList:
        taglist = JsonDeserializer().get_taglist()

        sevendays = timedelta(days=7)
        if taglist is None or taglist.lastupdate + sevendays < datetime.now():
            taglistapi = listapi.query_taglist()
            taglist = TagList.from_default([ taginternal["name"] for taginternal in taglistapi ])
            JsonSerializer().serialize_taglist(taglist)

        if not filter is None:
            taglist.filter(filter)
            
        return taglist
    
    def favorites_add_stationtolist(self, stationuuid:UUID, favlistuuid:UUID) -> None:
        station = self.__radiostations.get_station(stationuuid)

        if station is None:
            radiostationapi = stationapi.query_station(stationuuid)

            station = RadioStation.from_default(radiostationapi.stationuuid,
                                   radiostationapi.name,
                                   radiostationapi.url_resolved,
                                   radiostationapi.codec,                                   
                                   radiostationapi.countrycode,
                                   radiostationapi.languagecodes,
                                   radiostationapi.homepage,
                                   None if utils.str_isnullorwhitespace(radiostationapi.favicon) else httpcontent.get_urlbinary_content_as_base64(radiostationapi.favicon),
                                   None if utils.str_isnullorwhitespace(radiostationapi.favicon) else path.splitext(radiostationapi.favicon)[1][1:],
                                   radiostationapi.bitrate,
                                   list(radiostationapi.tags))

        self.__favorites.get_list(favlistuuid).add_station(station)
        self.__radiostations.add_station(station)

        JsonSerializer().serialize_radiostations(self.__radiostations)
        JsonSerializer().serialize_favorites(self.__favorites)

    def favorites_remove_stationfromlist(self, stationuuid:UUID, favlistuuid:UUID) -> None:
        station = self.__radiostations.get_station(stationuuid)

        self.__favorites.get_list(favlistuuid).remove_station(station)
        JsonSerializer().serialize_favorites(self.__favorites)

        self.stations_deletestation(station.uuid)
    
    def favorites_getlists(self) -> tuple:
        return self.__favorites.favoritelists
    
    def favorites_addlist(self) -> FavoriteList:
        favoritelist = self.__favorites.add_favoritelist()
        JsonSerializer().serialize_favorites(self.__favorites)
        return favoritelist
    
    def favorites_deletelist(self, uuid:UUID) -> FavoriteList:
        favlist = self.__favorites.get_list(uuid)
        station_uuids = []
        if not favlist is None:
            for stationentry in favlist.stations:
                station_uuids.append(stationentry.radiostation.uuid)

        self.__favorites.delete_favoritelist(uuid)
        JsonSerializer().serialize_favorites(self.__favorites)

        for station_uuid in station_uuids:
            self.stations_deletestation(station_uuid, False)

        JsonSerializer().serialize_radiostations(self.__radiostations)

    def favorites_getdefaultlist(self) -> FavoriteList:
        return self.__favorites.get_default()
    
    def favorites_getlist(self, listuuid:UUID) -> FavoriteList:
        return self.__favorites.get_list(listuuid)

    def favorites_get_any_station(self,) -> RadioStation:
        return self.__favorites.get_any_station()
    
    def favorites_changelistproperty(self, uuid:UUID, property:str, value:str) -> None:
        if property == "isdefault":
            self.__favorites.change_default(uuid, True if value.strip().lower() == "true" else False)
        elif property == "name":
            changelist = self.__favorites.get_list(uuid)
            changelist.name = value
        else: 
            raise TypeError(f"Change of property \"{property}\" supported.")
        
        JsonSerializer().serialize_favorites(self.__favorites)

    def favorites_movelist(self, uuid:UUID, direction:str) -> None:
        direction = Direction[direction]
        self.__favorites.move_list(uuid, direction)
        
        JsonSerializer().serialize_favorites(self.__favorites)

    def favorites_move_station_in_list(self, favlistuuid:UUID, stationuuid:UUID, direction:str) -> None:
        direction = Direction[direction]
        self.__favorites.move_station_in_list(favlistuuid, stationuuid, direction)
        
        JsonSerializer().serialize_favorites(self.__favorites)

    def settings_runontouch(self) -> bool:
        return self.__settings.usersettings.touch_runontouch
    
    def settings_web_defaultlanguage(self) -> bool:
        return self.__settings.usersettings.web_defaultlanguage
    
    def settings_web_defaultcountry(self) -> bool:
        return self.__settings.usersettings.web_defaultcountry
    
    def settings_touch_startwith(self) -> StartWith:
        return self.__settings.usersettings.touch_startwith
    
    def settings_set_touch_startwith(self, startwith:StartWith) -> None:
        self.__settings.usersettings.touch_startwith = startwith
        JsonSerializer().serialize_usersettings(self.__settings.usersettings)

    def settings_touch_laststation(self) -> UUID:
        return self.__settings.usersettings.touch_laststation
    
    def settings_changeproperty(self, property:str, value:str) -> None:
        if property == "country":
            countrylist = self.countries_get()

            if value in countrylist.countrylist.values() or value == "nofilter":
                self.__settings.usersettings.web_defaultcountry = value
        elif property == "lang":
            languagelist = self.languages_get()

            if value in languagelist.languagelist or value == "nofilter":
                self.__settings.usersettings.web_defaultlanguage = value
        else: 
            raise TypeError(f"Change of property \"{property}\" supported.")
        
        JsonSerializer().serialize_usersettings(self.__settings.usersettings)

    def radio_play(self, station_uuid:UUID = None) -> None:
        station = self.__radiostations.get_station(station_uuid)
        Vlc().play(station)
        
        if not station is None:
            original_laststation = self.__settings.usersettings.touch_laststation
            self.__settings.usersettings.touch_laststation = station.uuid

            if not original_laststation is None:
                self.stations_deletestation(original_laststation)

            JsonSerializer().serialize_usersettings(self.__settings.usersettings)
        else:
            station = Vlc().currentstation

        if RaspiFM().settings_runontouch(): #otherwise we are on dev most propably so we don't send a click on every play
            stationapi.send_stationclicked(station.uuid)

    def radio_isplaying(self) -> bool:
        return Vlc().isplaying
    
    def radio_currentstation(self) -> RadioStation:
        return Vlc().currentstation

    def radio_set_currentstation(self, station_uuid:UUID) -> None:
        station = self.__radiostations.get_station(station_uuid)
        Vlc().currentstation = station

        original_laststation = self.__settings.usersettings.touch_laststation
        self.__settings.usersettings.touch_laststation = station.uuid

        if not original_laststation is None:
            self.stations_deletestation(original_laststation)

        JsonSerializer().serialize_usersettings(self.__settings.usersettings)

    def radio_setvolume(self, volume:int) -> None:
        Vlc().volume = volume
        self.__settings.usersettings.touch_volume = volume
        JsonSerializer().serialize_usersettings(self.__settings.usersettings)

    def http_get_urlbinary_content_asb64(self, url:str) ->str:
        return httpcontent.get_urlbinary_content_as_base64(url)

    def radio_getvolume(self) -> int:
        return Vlc().volume

    def radio_getmeta(self) -> str:
        return Vlc().getmeta()

    def raspifm_shutdown(self) -> None:
        Vlc().shutdown()

    def radio_send_stationclicked(self, station_uuid:UUID) -> None:
        stationapi.send_stationclicked(station_uuid)

    def spotify_isplaying(self) -> bool:
        return Spotify().isplaying
    
    def spotify_set_isplaying(self, playing:bool) -> None:
        Spotify().isplaying = playing

    def spotify_currentplaying(self) -> SpotifyInfo:
        return Spotify().currentlyplaying

    def raspifm_getversion(self) -> str:
        return self.version