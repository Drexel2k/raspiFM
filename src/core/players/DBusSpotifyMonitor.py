from __future__ import annotations

from collections import deque
from queue import Queue
import socket
from threading import Thread
import traceback
from jeepney import DBusAddress, new_method_call, MatchRule, message_bus, HeaderFields
from jeepney.io.blocking import Proxy, DBusConnection
from jeepney.io.common import FilterHandle
from jeepney.io.blocking import open_dbus_connection

from common import socketstrings, utils
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
        self.__dbus_spotify_filter = None

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
                return self.__extract_metadata(dbus_spotify_metadata_reply.body[0][1])
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
        try:
            previous_meta = None
            run = True
            while run:
                current_meta = None
                signal_message = None
                send_message = None
                try:
                    signal_message = self.__dbus_connection.recv_until_filtered(self.__dbus_queue)
                #only solution found to unblock the recv_until_filtered call
                except ConnectionResetError as e:
                    if e.errno == 104:
                        run = False
                        continue
                
                send_message = False
                if signal_message.header.fields[HeaderFields.path] == "/org/mpris/MediaPlayer2":
                    #spotify state changed
                    
                    if not (dbusstrings.spotifydpropertyplaybackstatus in signal_message.body[1] or dbusstrings.spotifydpropertymetadata in signal_message.body[1]):
                        continue
                    
                    send_message = True
                    current_meta = self.__get_meta_from_change_properties(signal_message.body[1])

                if signal_message.header.fields[HeaderFields.path] == "/org/freedesktop/DBus":
                    servicename = signal_message.body[0]
                    newowner = signal_message.body[1]
                    oldowner = signal_message.body[2]

                    if servicename.startswith("org.mpris.MediaPlayer2.spotifyd.instance"):
                        #service new on the bus
                        send_message = True
                        if utils.str_isnullorwhitespace(newowner):
                            self.__spotify_dbusname = servicename
                            self.__spotify_service_presence_change()
                            current_meta = self.get_spotify_status()
                        #service left bus
                        if utils.str_isnullorwhitespace(oldowner):
                            self.__spotify_dbusname = None
                            self.__spotify_service_presence_change()
                            current_meta = None
                
                if send_message:
                    if current_meta != previous_meta:
                        previous_meta = current_meta
                        self.__message_queue.put(RaspiFMMessage({
                                                                    "message":"spotify_change",
                                                                    "args":{
                                                                                "spotify_currently_playing":current_meta
                                                                            }
                                                                }))
        except:
            run = False
            self.__message_queue.put(RaspiFMMessage({
                                                        "message":socketstrings.shutdown_string,
                                                        "args":{
                                                                "reason":traceback.format_exc()
                                                                }
                                                    }))

    def __spotify_service_presence_change(self) -> None:
        if self.__spotify_dbusname is None:
            self.__dbus_spotify_filter.close()
        else:
            dbus_spotify_address = DBusAddress(dbusstrings.spotifydpath, self.__spotify_dbusname, dbusstrings.dbuspropertiesinterface)
            dbus_spotify_changed_match_rule = MatchRule(
                    type="signal",
                    interface=dbus_spotify_address.interface,
                    member=dbusstrings.dbussignalpropertieschanged,
                    path=dbus_spotify_address.object_path
                    )
                
            self.__dbus_proxy.AddMatch(dbus_spotify_changed_match_rule)
            self.__dbus_spotify_filter = self.__dbus_connection.filter(dbus_spotify_changed_match_rule, queue=self.__dbus_queue)

    def __get_meta_from_change_properties(self, changeproperties:dict) -> dict:
        #if spotify is resumed after paused it sends only playing status
        if dbusstrings.spotifydpropertyplaybackstatus in changeproperties:
            if changeproperties[dbusstrings.spotifydpropertyplaybackstatus][1] == "Playing":
                return self.get_spotify_status()

        #on track change while playing spotify sends metadata
        if dbusstrings.spotifydpropertymetadata in changeproperties:
            return self.__extract_metadata(changeproperties[dbusstrings.spotifydpropertymetadata][1])

        return None
    
    def __extract_metadata(self, message_meta):
        return {
                    "title":message_meta[dbusstrings.spotifydmetadatatitle][1],
                    "album":message_meta[dbusstrings.spotifydmetadataalbum][1],
                    "artists":message_meta[dbusstrings.spotifydmetadataartists][1],
                    "arturl":message_meta[dbusstrings.spotifydmetadataarturl][1]}

    def stop_spotify(self) -> None:
        if not self.__spotify_dbusname is None:
            dbus_spotify_address = DBusAddress(dbusstrings.spotifydpath, self.__spotify_dbusname, dbusstrings.spotifydinterface)
            dbus_spotify_playbackstatus_message = new_method_call(dbus_spotify_address, dbusstrings.spotifydmethodpause, None, None)
            self.__dbus_connection.send(dbus_spotify_playbackstatus_message)

    def shutdown(self) -> None:
        #only solution found to unblock the recv_until_filtered call
        self.__dbus_connection.sock.shutdown(socket.SHUT_RDWR)