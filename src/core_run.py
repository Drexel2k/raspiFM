from threading import Thread
from queue import Queue
from uuid import UUID

from common import strings
from core.RaspiFM import RaspiFM
from core.socket.SocketManager import SocketManager

read_queue = Queue()
write_queue = Queue()
socket_manager = SocketManager(read_queue, write_queue)
socket_read_thread = Thread(target=socket_manager.create_server_socket)
socket_read_thread.start()

socket_write_thread = Thread(target=socket_manager.write)
socket_write_thread.start()

raspifm = RaspiFM()

while True:
    message_response = read_queue.get()
    #the server expects only queries  and no reponses
    #in the read queue as it doesn't send any queries
    #which expect a response.
    if message_response.response is None:
        func = getattr(raspifm, message_response.message[strings.message_string][strings.message_string])

        if message_response.message[strings.message_string][strings.message_string] in ["radio_play"]:
            if message_response.message[strings.message_string][strings.message_string] == "radio_play":
                func(UUID(message_response.message[strings.message_string][strings.args_string]["station_uuid"]))
        else:
            result_object = None
            if message_response.message[strings.message_string][strings.args_string] is None:
                result_object = func()
            else:
                result_object = func(**message_response.message[strings.message_string][strings.args_string])

            result_json_serializable = None

            #todo:make this somehow more maintainable...
            if message_response.message[strings.message_string][strings.message_string] == "favorites_getlists":
                result_json_serializable = [favorite_list.to_dict() for favorite_list in result_object]
            else:
                result_json_serializable = result_object

            message_response.response = {strings.result_string:result_json_serializable}

            write_queue.put(message_response)