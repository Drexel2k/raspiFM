from __future__ import annotations

from logging import Logger
import logging
import traceback
from queue import Queue
from threading import Thread
from uuid import UUID
from urllib.error import URLError

from common import log, socketstrings, utils
from common.socket.MessageResponse import MessageResponse
from core.RaspiFM import RaspiFM
from core.RaspiFMMessage import RaspiFMMessage
from core.StartWith import StartWith
from core.business.InvalidOperationError import InvalidOperationError
from core.players.VlcRadioMonitor import VlcRadioMonitor
from core.players.DBusSpotifyMonitor import DBusSpotifyMonitor
from core.players.SpotifyInfo import SpotifyInfo
from core.socket.SocketManager import SocketManager

class RaspiFMMessageManager:
    __slots__ = ["__clients_with_spotify_update_subscriptions", "__socket_manager", "__socket_timeout", "__logger"]
    __instance:RaspiFMMessageManager = None
    __clients_with_spotify_update_subscriptions:list
    __socket_manager:SocketManager
    __socket_timeout:float
    __logger:Logger

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(RaspiFMMessageManager, cls).__new__(cls)
            cls.__instance.__init()
        return cls.__instance
    
    def __init(self):
        self.__logger = logging.getLogger(log.core_logger_name)
        self.__socket_manager = None
        self.__clients_with_spotify_update_subscriptions = []
        self.__socket_timeout = 5

    def handle_messages(self, raspifm:RaspiFM, raspifm_call_queue:Queue) -> None:
        try:
            write_queue = Queue()
            self.__socket_manager = SocketManager(raspifm_call_queue, write_queue, self.socket_closed, logger=self.__logger)
            server_socket_read_thread = Thread(target=self.__socket_manager.read)
            server_socket_read_thread.start()

            socket_write_thread = Thread(target=self.__socket_manager.write)
            socket_write_thread.start()

            run = True
            while run:
                raspifm_call = raspifm_call_queue.get()
                if isinstance(raspifm_call, MessageResponse):
                    #the server expects only queries and no reponses
                    #in the read queue as it doesn't send any queries
                    #which expect a response.
                    if not self.__logger is None:
                        self.__logger.info(f"Received message: {raspifm_call.message[socketstrings.message_string][socketstrings.message_string]}")

                    if raspifm_call.response is None:
                        #special calls which are not addressed to raspiFM core
                        if raspifm_call.message[socketstrings.message_string][socketstrings.message_string] in ["players_status_subscribe",
                                                                                                                "raspifm_shutdown"]:
                            if raspifm_call.message[socketstrings.message_string][socketstrings.message_string] == "players_status_subscribe":
                                self.__clients_with_spotify_update_subscriptions.append(raspifm_call.socket_address)

                            raspifm_call.response = {socketstrings.result_string: None }
                            write_queue.put(raspifm_call)

                            #todo: unify waiting and exception checking which exists over several classes
                            if not raspifm_call.message_sent.wait(self.__socket_timeout):
                                raise Exception("raspifm core socket timeout")

                            if not raspifm_call.transfer_exception is None:
                                raise raspifm_call.transfer_exception

                            if raspifm_call.message[socketstrings.message_string][socketstrings.message_string] == "raspifm_shutdown":
                                run = False
                                self.__shutdown_all("Shutdown by service request, probably touchUI shutdown.")
                        else:
                            try:
                                func = getattr(raspifm, raspifm_call.message[socketstrings.message_string][socketstrings.message_string])

                                result_object = None

                                if raspifm_call.message[socketstrings.message_string][socketstrings.args_string] is None:
                                    result_object = func()                                 
                                else:
                                    result_object = func(**RaspiFMMessageManager.deserialize_arguments(raspifm_call.message[socketstrings.message_string][socketstrings.message_string], raspifm_call.message[socketstrings.message_string][socketstrings.args_string]))

                            except (URLError, AttributeError) as app_exception:
                                if not self.__logger is None:
                                    self.__logger.error(traceback.print_exc())

                                raspifm_call.response_exception = app_exception
                            except InvalidOperationError as InvalidOperationError_exception:
                                raspifm_call.response_exception = InvalidOperationError_exception

                            if raspifm_call.response_exception is None:      
                                raspifm_call.response = {socketstrings.result_string: None if result_object is None else RaspiFMMessageManager.serialize_result_object(raspifm_call.message[socketstrings.message_string][socketstrings.message_string], result_object)}

                            if not self.__logger is None:
                                if self.__logger.level <= logging.DEBUG:
                                    self.__logger.debug(f"Response: {raspifm_call.response}, exception: {raspifm_call.response_exception}")
                                else:
                                    self.__logger.info(f"Response to: {raspifm_call.message[socketstrings.message_string][socketstrings.message_string]} ready, exception: {raspifm_call.response_exception}")

                            write_queue.put(raspifm_call)

                            if not raspifm_call.message_sent.wait(self.__socket_timeout):
                                raise Exception("raspifm core socket timeout")

                            if not raspifm_call.transfer_exception is None:
                                raise raspifm_call.transfer_exception
                        
                if  isinstance(raspifm_call, RaspiFMMessage):
                    if raspifm_call.message[socketstrings.message_string] == "spotify_change":
                        func = getattr(raspifm, raspifm_call.message[socketstrings.message_string])
                        #actually, only the isplaying information must be saved here, as the only location where
                        #currentlyplaying info is needed is a few lines later: spotify_currently_playing = RaspiFM().spotify_currently_playing()
                        #todo: maybe change it in the future
                        if raspifm_call.message[socketstrings.args_string]["spotify_currently_playing"] is None:
                            func(None)
                        else:
                            func(SpotifyInfo(**raspifm_call.message[socketstrings.args_string]["spotify_currently_playing"]))

                        #not every client needs radio players updates,
                        #e.g. the web client which is only for favorites management doesn't nee these updates.
                        for client_socket_address in self.__clients_with_spotify_update_subscriptions:
                            spotify_currently_playing = RaspiFM().spotify_currently_playing()
                            self.__socket_manager.send_message_to_client(client_socket_address, raspifm_call.message[socketstrings.message_string], {"spotify_currently_playing": None if spotify_currently_playing is None else spotify_currently_playing.to_dict()})

                    if raspifm_call.message[socketstrings.message_string] == "radio_change":
                        #not every client needs radio players updates,
                        #e.g. the web client which is only for favorites management doesn't nee these updates.
                        for client_socket_address in self.__clients_with_spotify_update_subscriptions:
                            self.__socket_manager.send_message_to_client(client_socket_address, raspifm_call.message[socketstrings.message_string], raspifm_call.message[socketstrings.args_string])

                    if raspifm_call.message[socketstrings.message_string] == socketstrings.shutdown_string:
                        run = False
                        self.__shutdown_all(raspifm_call.message[socketstrings.args_string]["reason"])
        except:
            self.__shutdown_all(traceback.format_exc())

    def __shutdown_all(self, reason:str) -> None:
        try:
            VlcRadioMonitor().stop_meta_getter()
            DBusSpotifyMonitor().shutdown()
            self.__socket_manager.shutdown()

            if not utils.str_isnullorwhitespace(reason):
                if not self.__logger is None:
                    self.__logger.info(f"Shutting down core due to: {reason}")
        except:
            if not utils.str_isnullorwhitespace(reason):
                if not self.__logger is None:
                    self.__logger.error(f"Core shutdown error: {traceback.format_exc()}")
        
    @staticmethod
    def deserialize_arguments(method_name:str, method_arguments:dict) -> dict:
        deserialized_arguments = {}

        if method_name == "radio_play":
            deserialized_arguments["station_uuid"] = None if method_arguments["station_uuid"] is None else UUID(method_arguments["station_uuid"])
        elif method_name in ["radio_set_currentstation", "stations_getstation"]:
            deserialized_arguments["station_uuid"] = UUID(method_arguments["station_uuid"])
        elif method_name == "settings_set_touch_startwith":
            deserialized_arguments["startwith"] = StartWith(method_arguments["startwith"])
        elif method_name in ["favorites_add_stationtolist", "favorites_remove_stationfromlist"]:
            deserialized_arguments["station_uuid"] = UUID(method_arguments["station_uuid"])
            deserialized_arguments["favlist_uuid"] = UUID(method_arguments["favlist_uuid"])
        elif method_name == "favorites_changelistproperty":
            deserialized_arguments["favlist_uuid"] = UUID(method_arguments["favlist_uuid"])
            deserialized_arguments["property"] = method_arguments["property"]
            deserialized_arguments["value"] = method_arguments["value"]
        elif method_name in ["favorites_deletelist", "favorites_getlist"]:
            deserialized_arguments["favlist_uuid"] = UUID(method_arguments["favlist_uuid"])
        elif method_name == "favorites_movelist":
            deserialized_arguments["favlist_uuid"] = UUID(method_arguments["favlist_uuid"])
            deserialized_arguments["direction"] = method_arguments["direction"]
        elif method_name == "favorites_move_station_in_list":
            deserialized_arguments["favlist_uuid"] = UUID(method_arguments["favlist_uuid"])
            deserialized_arguments["station_uuid"] = UUID(method_arguments["station_uuid"])
            deserialized_arguments["direction"] = method_arguments["direction"]
        else:
            deserialized_arguments = method_arguments
        
        return deserialized_arguments
    
    @staticmethod
    def serialize_result_object(method_name:str, result_object:dict) -> dict:
        serialized_result_object = {}

        if method_name in ["stations_getstation",
                            "favorites_getdefaultlist",
                            "favorites_get_any_station",
                            "radio_get_currentstation",
                            "spotify_currently_playing",
                            "favorites_getlist",
                            "favorites_addlist"]:
            serialized_result_object = result_object.to_dict()
        elif method_name == "settings_touch_laststation":
            serialized_result_object = str(result_object)
        elif method_name == "favorites_getlists":
            serialized_result_object = [favorite_list.to_dict() for favorite_list in result_object]
        elif method_name in ["settings_touch_startwith",
                                "settings_all_loglevel"]:
            serialized_result_object = result_object.value
        elif method_name == "countries_get":
            serialized_result_object = result_object.countrylist
        elif method_name == "languages_get":
            serialized_result_object = result_object.languagelist
        elif method_name == "stationapis_get":
            serialized_result_object = [radiostationapi.to_dict() for radiostationapi in result_object]
        elif method_name == "tags_get":
            serialized_result_object = result_object.taglist
        else:
            serialized_result_object = result_object
        
        return serialized_result_object
                                
    def socket_closed(self, socket_address:str) -> None:
        if socket_address in self.__clients_with_spotify_update_subscriptions:
            self.__clients_with_spotify_update_subscriptions.remove(socket_address)