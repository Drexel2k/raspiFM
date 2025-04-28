from PyQt6.QtCore import pyqtSignal, QRunnable

from touchui.socket.SocketManager import SocketManager

class CoreMonitor(QRunnable):
    __slots__ = ["__socket_manager"]
    __socket_manager:SocketManager

    core_notification_available = pyqtSignal(dict)

    def __init__(self, socket_manager:SocketManager):
        super().__init__()
        self.__socket_manager = socket_manager

    def run(self) -> None:
        self.__socket_manager.monitor_read_queue()