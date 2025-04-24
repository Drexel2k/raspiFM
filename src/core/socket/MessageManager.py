from queue import Queue
from threading import Thread
from uuid import UUID

from common import strings
from core.RaspiFM import RaspiFM
from core.StartWith import StartWith
from core.players.SpotifyInfo import SpotifyInfo
from core.socket.SocketManager import SocketManager

class MessageManager:
    @staticmethod
    def handle_messages(raspifm:RaspiFM) -> None:
        read_queue = Queue()
        write_queue = Queue()
        socket_manager = SocketManager(read_queue, write_queue)
        socket_read_thread = Thread(target=socket_manager.create_server_socket)
        socket_read_thread.start()

        socket_write_thread = Thread(target=socket_manager.write)
        socket_write_thread.start()

        while True:
            message_response = read_queue.get()
            #the server expects only queries and no reponses
            #in the read queue as it doesn't send any queries
            #which expect a response.
            if message_response.response is None:
                func = getattr(raspifm, message_response.message[strings.message_string][strings.message_string])

                #queries which don't send responses
                if message_response.message[strings.message_string][strings.message_string] in ["radio_play", "radio_set_currentstation", "radio_send_stationclicked", "radio_stop", "radio_setvolume", "settings_set_touch_startwith", "spotify_set_currentplaying", "spotify_set_isplaying", "raspifm_shutdown"]:
                    #queries which require argument conversion
                    if message_response.message[strings.message_string][strings.message_string] == "radio_play":
                        func(None if message_response.message[strings.message_string][strings.args_string]["station_uuid"] is None else UUID(message_response.message[strings.message_string][strings.args_string]["station_uuid"]))
                    elif message_response.message[strings.message_string][strings.message_string] == "radio_set_currentstation":
                        func(UUID(message_response.message[strings.message_string][strings.args_string]["station_uuid"]))
                    elif message_response.message[strings.message_string][strings.message_string] == "radio_send_stationclicked":
                        func(UUID(message_response.message[strings.message_string][strings.args_string]["station_uuid"]))
                    elif message_response.message[strings.message_string][strings.message_string] == "settings_set_touch_startwith":
                        func(StartWith(message_response.message[strings.message_string][strings.args_string]["startwith"]))
                    elif message_response.message[strings.message_string][strings.message_string] == "spotify_set_currentplaying":
                        func(SpotifyInfo(**message_response.message[strings.message_string][strings.args_string]["info"]))
                    else:
                        if message_response.message[strings.message_string][strings.args_string] is None:
                            func()
                        else:
                            func(**message_response.message[strings.message_string][strings.args_string])
                else:
                    result_object = None
                    if message_response.message[strings.message_string][strings.args_string] is None:
                        result_object = func()
                    else:
                        #queries which require argument conversion
                        if message_response.message[strings.message_string][strings.message_string] == "stations_getstation":
                            result_object = func(UUID(message_response.message[strings.message_string][strings.args_string]["station_uuid"]))
                        else:
                            result_object = func(**message_response.message[strings.message_string][strings.args_string])

                    result_json_serializable = None
                    if not result_object is None:
                        #queries which require result conversion
                        if message_response.message[strings.message_string][strings.message_string] in ["stations_getstation", "favorites_getdefaultlist", "favorites_get_any_station", "radio_currentstation", "spotify_currentplaying"]:
                            result_json_serializable = result_object.to_dict()
                        elif message_response.message[strings.message_string][strings.message_string] == "favorites_getlists":
                            result_json_serializable = [favorite_list.to_dict() for favorite_list in result_object]
                        elif message_response.message[strings.message_string][strings.message_string] == "settings_touch_startwith":
                            result_json_serializable = result_object.value
                        elif message_response.message[strings.message_string][strings.message_string] == "settings_touch_laststation":
                            result_json_serializable = str(result_object)
                        else:
                            result_json_serializable = result_object

                    message_response.response = {strings.result_string:result_json_serializable}

                    write_queue.put(message_response)