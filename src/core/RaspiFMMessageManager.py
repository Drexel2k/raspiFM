from __future__ import annotations

from queue import Queue
from threading import Thread
from uuid import UUID

from common import strings
from common.socket.MessageResponse import MessageResponse
from core.players.DBusSpotifyMonitor import DBusSpotifyMonitor
from core.RaspiFM import RaspiFM
from core.RaspiFMMessage import RaspiFMMessage
from core.StartWith import StartWith
from core.players.SpotifyInfo import SpotifyInfo
from core.socket.SocketManager import SocketManager

class RaspiFMMessageManager:
    __slots__ = ["__clients_with_spotify_update_subscriptions"]
    __instance:RaspiFMMessageManager = None
    __clients_with_spotify_update_subscriptions:list

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(RaspiFMMessageManager, cls).__new__(cls)
            cls.__instance.__init()
        return cls.__instance
    
    def __init(self):
        self.__clients_with_spotify_update_subscriptions = []

    def handle_messages(self, raspifm:RaspiFM, raspifm_call_queue:Queue) -> None:
        write_queue = Queue()
        socket_manager = SocketManager(raspifm_call_queue, write_queue, self.socket_closed)
        server_socket_read_thread = Thread(target=socket_manager.read)
        server_socket_read_thread.start()

        socket_write_thread = Thread(target=socket_manager.write)
        socket_write_thread.start()

        while True:
            raspifm_call = raspifm_call_queue.get()
            if type(raspifm_call) is MessageResponse:
                #the server expects only queries and no reponses
                #in the read queue as it doesn't send any queries
                #which expect a response.
                if raspifm_call.response is None:
                    if raspifm_call.message[strings.message_string][strings.message_string] == "players_status_subscribe":
                        self.__clients_with_spotify_update_subscriptions.append(raspifm_call.socket_address)
                        continue

                    func = getattr(raspifm, raspifm_call.message[strings.message_string][strings.message_string])

                    #queries which don't send responses
                    if raspifm_call.message[strings.message_string][strings.message_string] in ["radio_play",
                                                                                                "radio_set_currentstation",
                                                                                                "radio_stop",
                                                                                                "radio_setvolume",
                                                                                                "settings_set_touch_startwith",
                                                                                                "spotify_set_currentplaying",
                                                                                                "spotify_set_isplaying",
                                                                                                "raspifm_shutdown",
                                                                                                "spotify_stop",
                                                                                                "favorites_add_stationtolist",
                                                                                                "favorites_remove_stationfromlist",
                                                                                                "favorites_changelistproperty",
                                                                                                "favorites_deletelist",
                                                                                                "favorites_movelist",
                                                                                                "favorites_move_station_in_list",
                                                                                                "settings_changeproperty"]:
                        #queries which require argument conversion
                        if raspifm_call.message[strings.message_string][strings.message_string] == "radio_play":
                            func(None if raspifm_call.message[strings.message_string][strings.args_string]["station_uuid"] is None else UUID(raspifm_call.message[strings.message_string][strings.args_string]["station_uuid"]))
                        elif raspifm_call.message[strings.message_string][strings.message_string] == "radio_set_currentstation":
                            func(UUID(raspifm_call.message[strings.message_string][strings.args_string]["station_uuid"]))
                        elif raspifm_call.message[strings.message_string][strings.message_string] == "settings_set_touch_startwith":
                            func(StartWith(raspifm_call.message[strings.message_string][strings.args_string]["startwith"]))
                        elif raspifm_call.message[strings.message_string][strings.message_string] == "spotify_set_currentplaying":
                            func(SpotifyInfo(**raspifm_call.message[strings.message_string][strings.args_string]["info"]))
                        elif raspifm_call.message[strings.message_string][strings.message_string] in ["favorites_add_stationtolist", "favorites_remove_stationfromlist"]:
                            func(UUID(raspifm_call.message[strings.message_string][strings.args_string]["station_uuid"]), UUID(raspifm_call.message[strings.message_string][strings.args_string]["favlist_uuid"]))
                        elif raspifm_call.message[strings.message_string][strings.message_string] == "favorites_changelistproperty":
                            result_object = func(UUID(raspifm_call.message[strings.message_string][strings.args_string]["favlist_uuid"]),raspifm_call.message[strings.message_string][strings.args_string]["property"],raspifm_call.message[strings.message_string][strings.args_string]["value"])
                        elif raspifm_call.message[strings.message_string][strings.message_string] == "favorites_deletelist":
                            result_object = func(UUID(raspifm_call.message[strings.message_string][strings.args_string]["favlist_uuid"]))
                        elif raspifm_call.message[strings.message_string][strings.message_string] == "favorites_movelist":
                            result_object = func(UUID(raspifm_call.message[strings.message_string][strings.args_string]["favlist_uuid"]), raspifm_call.message[strings.message_string][strings.args_string]["direction"])
                        elif raspifm_call.message[strings.message_string][strings.message_string] == "favorites_move_station_in_list":
                            result_object = func(UUID(raspifm_call.message[strings.message_string][strings.args_string]["favlist_uuid"]), UUID(raspifm_call.message[strings.message_string][strings.args_string]["station_uuid"]), raspifm_call.message[strings.message_string][strings.args_string]["direction"])
                        else:
                            if raspifm_call.message[strings.message_string][strings.args_string] is None:
                                func()
                            else:
                                func(**raspifm_call.message[strings.message_string][strings.args_string])
                    else:
                        result_object = None
                        if raspifm_call.message[strings.message_string][strings.args_string] is None:
                            result_object = func()
                        else:
                            #queries which require argument conversion
                            if raspifm_call.message[strings.message_string][strings.message_string] == "stations_getstation":
                                result_object = func(UUID(raspifm_call.message[strings.message_string][strings.args_string]["station_uuid"]))
                            elif raspifm_call.message[strings.message_string][strings.message_string] == "favorites_getlist":
                                result_object = func(UUID(raspifm_call.message[strings.message_string][strings.args_string]["favlist_uuid"]))
                            else:
                                result_object = func(**raspifm_call.message[strings.message_string][strings.args_string])

                        result_json_serializable = None
                        if not result_object is None:
                            #queries which require result conversion
                            if raspifm_call.message[strings.message_string][strings.message_string] in ["stations_getstation",
                                                                                                        "favorites_getdefaultlist",
                                                                                                        "favorites_get_any_station",
                                                                                                        "radio_get_currentstation",
                                                                                                        "spotify_currently_playing",
                                                                                                        "favorites_getlist",
                                                                                                        "favorites_addlist"]:
                                result_json_serializable = result_object.to_dict()
                            elif raspifm_call.message[strings.message_string][strings.message_string] == "settings_touch_laststation":
                                result_json_serializable = str(result_object)
                            elif raspifm_call.message[strings.message_string][strings.message_string] == "favorites_getlists":
                                result_json_serializable = [favorite_list.to_dict() for favorite_list in result_object]
                            elif raspifm_call.message[strings.message_string][strings.message_string] == "settings_touch_startwith":
                                result_json_serializable = result_object.value
                            elif raspifm_call.message[strings.message_string][strings.message_string] == "countries_get":
                                result_json_serializable = result_object.countrylist
                            elif raspifm_call.message[strings.message_string][strings.message_string] == "languages_get":
                                result_json_serializable = result_object.languagelist
                            elif raspifm_call.message[strings.message_string][strings.message_string] == "stationapis_get":
                                result_json_serializable = [radiostationapi.to_dict() for radiostationapi in result_object]
                            elif raspifm_call.message[strings.message_string][strings.message_string] == "tags_get":
                                result_json_serializable = result_object.taglist
                            else:
                                result_json_serializable = result_object

                        raspifm_call.response = {strings.result_string:result_json_serializable}

                        write_queue.put(raspifm_call)
                    
            #not every client needs radio players updates,
            #e.g. the web client which is only for favorites management doesn't nee these updates.
            if type(raspifm_call) is RaspiFMMessage:
                if raspifm_call.message[strings.message_string] == "spotify_change":
                    func = getattr(raspifm, raspifm_call.message[strings.message_string])
                    if raspifm_call.message[strings.args_string]["spotify_currently_playing"] is None:
                        func(None)
                    else:
                        func(SpotifyInfo(**raspifm_call.message[strings.args_string]["spotify_currently_playing"]))

                for client_socket_address in self.__clients_with_spotify_update_subscriptions:
                    if raspifm_call.message[strings.message_string] == "radio_change":
                        socket_manager.send_message_to_client(client_socket_address, raspifm_call.message[strings.message_string], raspifm_call.message[strings.args_string])
                    if raspifm_call.message[strings.message_string] == "spotify_change":
                        spotify_currently_playing = RaspiFM().spotify_currently_playing()
                        socket_manager.send_message_to_client(client_socket_address, raspifm_call.message[strings.message_string], {"spotify_currently_playing": None if spotify_currently_playing is None else spotify_currently_playing.to_dict()})
                                
    def socket_closed(self, socket_address:str) -> None:
        if socket_address in self.__clients_with_spotify_update_subscriptions:
            self.__clients_with_spotify_update_subscriptions.remove(socket_address)