import logging
from queue import Queue

import setproctitle

from common import log
from core.players.VlcRadioMonitor import VlcRadioMonitor
from core.players.DBusSpotifyMonitor import DBusSpotifyMonitor
from core.RaspiFM import RaspiFM
from core.RaspiFMMessageManager import RaspiFMMessageManager
from core.players.SpotifyInfo import SpotifyInfo

logger = log.init_logger(log.core_logger_name)

setproctitle.setproctitle("raspiFM core")

raspifm_call_queue = Queue()
VlcRadioMonitor(raspifm_call_queue)
DBusSpotifyMonitor(raspifm_call_queue)
spotify_status = DBusSpotifyMonitor().get_spotify_status()
raspifm = RaspiFM(None if spotify_status == None else SpotifyInfo(**spotify_status))

DBusSpotifyMonitor().monitor_dbus()
RaspiFMMessageManager()
RaspiFMMessageManager().handle_messages(raspifm, raspifm_call_queue)