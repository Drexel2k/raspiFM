from __future__ import annotations

from collections import deque
from queue import Queue
from threading import Thread
from jeepney import DBusAddress, new_method_call, MatchRule, message_bus, HeaderFields
from jeepney.io.blocking import Proxy, DBusConnection
from jeepney.io.common import FilterHandle
from jeepney.io.blocking import open_dbus_connection

from common import utils
from core.players import dbusstrings
from core.RaspiFMMessage import RaspiFMMessage

class DBusSpotifyMonitor:
    __slots__ = ["__message_queue", "__spotify_dbusname", "__dbus_spotify_filter", "__dbus_connection", "__dbus_queue", "__dbus_proxy"]
    __instance:DBusSpotifyMonitor = None
    __message_queue:Queue
    __dbus_spotify_filter:FilterHandle
    __dbus_connection:DBusConnection
    __dbus_queue:deque
    __dbus_proxy:Proxy
    __spotify_dbusname:str

    def __new__(cls, message_queue:Queue = None):
        if cls.__instance is None:
            if message_queue is None:
                raise ValueError("Missing argument on first call (initialization): message_queue")
            
            cls.__instance = super(DBusSpotifyMonitor, cls).__new__(cls)
            cls.__instance.__init(message_queue)
        return cls.__instance
    
    def __init(self, message_queue:Queue):
        self.__message_queue = message_queue
        self.__initializespotify()

    def monitor_dbus(self):
        socket_read_thread = Thread(target=self.__monitor_internal)
        socket_read_thread.start()

    def get_spotify_status(self) -> dict:
        if self.__spotify_dbusname is None:
            return None
        else:
            dbus_spotify_address = DBusAddress(dbusstrings.spotifydpath, self.__spotify_dbusname, dbusstrings.dbuspropertiesinterface)
            dbus_spotify_playbackstatus_message = new_method_call(dbus_spotify_address, dbusstrings.dbusmethodget, "ss", (dbusstrings.spotifydinterface, dbusstrings.spotifydpropertyplaybackstatus))

            dbus_spotify_playbackstatus_reply = self.__dbus_connection.send_and_get_reply(dbus_spotify_playbackstatus_message)
            if dbus_spotify_playbackstatus_reply.body[0][1] == "Playing":
                dbus_spotify_metadata_message = new_method_call(dbus_spotify_address, dbusstrings.dbusmethodget, "ss", (dbusstrings.spotifydinterface, dbusstrings.spotifydpropertymetadata))
                dbus_spotify_metadata_reply = self.__dbus_connection.send_and_get_reply(dbus_spotify_metadata_message)
                metadata = dbus_spotify_metadata_reply.body[0][1]
                return {
                            "title":metadata[dbusstrings.spotifydmetadatatitle][1],
                            "album":metadata[dbusstrings.spotifydmetadataalbum][1],
                            "artists":metadata[dbusstrings.spotifydmetadataartists][1],
                            "arturl":metadata[dbusstrings.spotifydmetadataarturl][1]}
            else:
                return None
            
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
            self.__spotify_service_presence_change()

    def __monitor_internal(self):
        previous_meta = {"-1":"-1"}
        while True:
            current_meta = None
            signal_message = self.__dbus_connection.recv_until_filtered(self.__dbus_queue)
            if signal_message.header.fields[HeaderFields.path] == "/org/mpris/MediaPlayer2":
                #spotify state changed
                current_meta = self.__get_meta_from_change_properties(signal_message.body[1])

            if signal_message.header.fields[HeaderFields.path] == "/org/freedesktop/DBus":
                servicename = signal_message.body[0]
                newowner = signal_message.body[1]
                oldowner = signal_message.body[2]

                if servicename.startswith("org.mpris.MediaPlayer2.spotifyd.instance"):
                    #service new on the bus
                    if utils.str_isnullorwhitespace(newowner):
                        self.__spotify_dbusname = servicename
                        self.__spotify_service_presence_change()
                        current_meta = self.get_spotify_status()
                    #service left bus
                    if utils.str_isnullorwhitespace(oldowner):
                        self.__spotify_dbusname = None
                        self.__spotify_service_presence_change()
                        current_meta = self.get_spotify_status()
            
            if current_meta != previous_meta:
                previous_meta = current_meta
                self.__message_queue.put(RaspiFMMessage({
                                                            "message":"spotify_change",
                                                            "args":{
                                                                        "spotify_metadata":current_meta}}))

    def __spotify_service_presence_change(self) -> None:
        if not self.__spotify_dbusname is None:
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

    def __get_meta_from_change_properties(self, changeproperties:dict) -> dict:
        #Sometimes, not reproducable, not alle infos are in the changeproperties, onyl one attribute like volume is in it.
        #Normaly after that another propertieschange signal comes in with the full infos.
        if not dbusstrings.spotifydpropertymetadata in changeproperties or not dbusstrings.spotifydpropertyplaybackstatus in changeproperties:
            return None

        if changeproperties[dbusstrings.spotifydpropertyplaybackstatus][1] == "Playing":
            metadata = changeproperties[dbusstrings.spotifydpropertymetadata][1]
            return {
                                                                            "title":metadata[dbusstrings.spotifydmetadatatitle][1],
                                                                            "album":metadata[dbusstrings.spotifydmetadataalbum][1],
                                                                            "artists":metadata[dbusstrings.spotifydmetadataartists][1],
                                                                            "arturl":metadata[dbusstrings.spotifydmetadataarturl][1]}

        return None
    
    def stop_spotify(self) -> None:
        if not self.__spotify_dbusname is None:
            dbus_spotify_address = DBusAddress(dbusstrings.spotifydpath, self.__spotify_dbusname, dbusstrings.spotifydinterface)
            dbus_spotify_playbackstatus_message = new_method_call(dbus_spotify_address, dbusstrings.spotifydmethodpause, None, None)
            self.__dbus_connection.send(dbus_spotify_playbackstatus_message)