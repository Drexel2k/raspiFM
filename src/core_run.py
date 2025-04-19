from threading import Thread
from queue import Queue

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

RaspiFM()
while True:
    message_response = read_queue.get()
    #the server expects only queries  and no reponses
    #in the read queue as it doesn't send any queries
    #which expect a response.
    if message_response.response is None:
        if message_response.message[strings.message_string][strings.message_string] == "spotify_isplaying":
            message_response.response = {strings.result_string: RaspiFM().spotify_isplaying()} 
        #todo: do something
    write_queue.put(message_response)