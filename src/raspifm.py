# Echo server program
import os
import socket
import selectors

from core.socket import SocketTransferManager

#No multi threading in selector mechanisms!
socket_selector = selectors.DefaultSelector()

def accept_wrapper(sock):
    conn, addr = sock.accept()
    conn.setblocking(False)
    socket_transfermanager = SocketTransferManager(socket_selector, conn, addr)
    socket_selector.register(conn, selectors.EVENT_READ, socket_transfermanager)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb += recv_data
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = sock.send(data.outb) 
            data.outb = data.outb[sent:]

socketpath = "/tmp/raspifm_socket"
raspifm_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
try:
    os.remove(socketpath)
except OSError:
    pass
raspifm_socket.bind(socketpath)
raspifm_socket.listen()
raspifm_socket.setblocking(False)
socket_selector.register(raspifm_socket, selectors.EVENT_READ, None)

while True:
    events = socket_selector.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            socket_transfermanager = key.data
            socket_transfermanager.process_events(mask)

socket_selector.close()

