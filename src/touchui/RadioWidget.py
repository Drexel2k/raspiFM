import base64
import time
from types import MethodType

from PyQt6.QtCore import Qt
from PyQt6.QtCore import QObject
from PyQt6.QtCore import QRunnable
from PyQt6.QtCore import QThreadPool
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QSlider

import vlc
from vlc import MediaPlayer

from .MarqueeLabel import MarqueeLabel
from ..core.raspifmcore import RaspiFM

class RadioWidget(QWidget):
    __slots__ = ["__vlcinstance", "__vlcplayer", "__vlcmedia", "__vlcgetmeta_enabled", "__playcontrolbutton", "__threadpool", "__infolabel"]
    __vlcinstance:vlc.Instance
    __vlcplayer: MediaPlayer
    __vlcmedia:vlc.Media
    __playcontrolbutton:QPushButton
    __infolabel:QLabel
    __vlcgetmeta_enabled:bool
    __threadpool:QThreadPool

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__threadpool = QThreadPool()
        initialvolume = 50

        main_layout_vertical = QVBoxLayout()
        self.setLayout(main_layout_vertical)
 
        stationimagelabel = QLabel()
        main_layout_vertical.addWidget(stationimagelabel, alignment = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.__infolabel = MarqueeLabel()
        self.__infolabel.setStyleSheet("QLabel { font-size:36px; }") #Font-size ist set in qt-material css and can only be overriden in css.
        main_layout_vertical.addWidget(self.__infolabel)

        playcontrolbutton = QPushButton("Stop")
        playcontrolbutton.clicked.connect(self.playcontrol_clicked)
        playcontrolbutton.setFixedWidth(100)
        self.__playcontrolbutton = playcontrolbutton
        main_layout_vertical.addWidget(playcontrolbutton, alignment = Qt.AlignmentFlag.AlignHCenter)

        main_layout_vertical.addStretch()

        volslider = QSlider(Qt.Orientation.Horizontal)
        volslider.sliderMoved.connect(self.volslider_moved)
        volslider.setValue(initialvolume)
        main_layout_vertical.addWidget(volslider)

        self.__vlcinstance = vlc.Instance()
        self.__vlcplayer = self.__vlcinstance.media_player_new()
        self.__vlcmedia = self.__vlcinstance.media_new(RaspiFM().favorites_getdefaultlist().stations[0].url)
        self.__vlcplayer.set_media(self.__vlcmedia)
        self.__vlcplayer.audio_set_volume(initialvolume)

        self.__vlcplayer.play()

        qx = QPixmap()
        qx.loadFromData(base64.b64decode(RaspiFM().favorites_getdefaultlist().stations[0].faviconb64), "PNG")
        stationimagelabel.setPixmap(qx)

        self.__vlcgetmeta_enabled = True
        self.startmediagetter()

    def startmediagetter(self):
        mediametagetter = MediaMetaGetter(self.getmeta)
        mediametagetter.infocallback.info.connect(self.updateinfo)
        self.__threadpool.start(mediametagetter)

    def playcontrol_clicked(self) -> None:
        if(self.__vlcplayer.is_playing()):
            self.__vlcgetmeta_enabled = False
            self.__vlcplayer.stop()
            self.__infolabel.setText(None)
            self.__playcontrolbutton.setText("Play")
        else:
            self.__vlcplayer.play()
            self.__vlcgetmeta_enabled = True
            self.startmediagetter()
            self.__playcontrolbutton.setText("Stop")

    def volslider_moved(self, value:int) -> None:
       self.__vlcplayer.audio_set_volume(value)

    def updateinfo(self, info:str):
        self.__infolabel.setText(info)

    def getmeta(self, infocallback:pyqtSignal) -> None: 
        previnfo= ""
        sleep = 5
        while self.__vlcgetmeta_enabled:
            time.sleep(sleep)
            print(sleep)
            if(sleep < 6):
                sleep = sleep + 5
            info = self.__vlcmedia.get_meta(vlc.Meta.NowPlaying) # vlc.Meta 12: 'NowPlaying', see vlc.py class Meta(_Enum)
            if info != previnfo:
                infocallback.emit(info)
                previnfo = info

class MetaSignal(QObject):
    info = pyqtSignal(str)

class MediaMetaGetter(QRunnable):

    def __init__(self, execute:MethodType):
        super().__init__()
        self.execute = execute
        self.infocallback = MetaSignal()

    @pyqtSlot()
    def run(self) ->None:
        self.execute(self.infocallback.info)
