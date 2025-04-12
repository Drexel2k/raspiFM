from threading import Thread
from queue import Queue

from core.socket.SocketManager import SocketManager

request_queue = Queue()
response_queue = Queue()
socket_manager = SocketManager(request_queue, response_queue)
socket_read_thread = Thread(target=socket_manager.create_server_socket)
socket_read_thread.start()

socket_write_thread = Thread(target=socket_manager.send_responses)
socket_write_thread.start()

while True:
    request_response = request_queue.get()
    #todo: do something
    response_queue.put(request_response)