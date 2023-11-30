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

from..core.Vlc import Vlc
from .MarqueeLabel import MarqueeLabel
from ..core.RaspiFM import RaspiFM

class RadioWidget(QWidget):
    __slots__ = ["__vlcgetmeta_enabled", "__btn_playcontrol", "__threadpool", "__lbl_info", "__volume"]

    __btn_playcontrol:QPushButton
    __lbl_nowplaying:MarqueeLabel
    __vlcgetmeta_enabled:bool
    __threadpool:QThreadPool
    __volume:int

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__threadpool = QThreadPool()
        self.__volume = 50
        main_layout_vertical = QVBoxLayout()
        self.setLayout(main_layout_vertical)
 
        stationimagelabel = QLabel()
        qx = QPixmap()
        qx.loadFromData(base64.b64decode(RaspiFM().favorites_getdefaultlist().stations[0].faviconb64), "PNG")
        stationimagelabel.setPixmap(qx)
        main_layout_vertical.addWidget(stationimagelabel, alignment = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.__lbl_nowplaying = MarqueeLabel()
        self.__lbl_nowplaying.setStyleSheet("QLabel { font-size:36px; }") #Font-size ist set in qt-material css and can only be overriden in css  
        main_layout_vertical.addWidget(self.__lbl_nowplaying, alignment=Qt.AlignmentFlag.AlignHCenter)

        main_layout_vertical.addStretch()

        playcontrolbutton = QPushButton("Stop")
        playcontrolbutton.clicked.connect(self.playcontrol_clicked)
        playcontrolbutton.setFixedWidth(100)
        self.__btn_playcontrol = playcontrolbutton
        main_layout_vertical.addWidget(playcontrolbutton, alignment = Qt.AlignmentFlag.AlignHCenter)

        volslider = QSlider(Qt.Orientation.Horizontal)
        volslider.sliderMoved.connect(self.volslider_moved)
        volslider.setValue(self.__volume)
        main_layout_vertical.addWidget(volslider)

        if(not Vlc().isplaying):
            Vlc().play(RaspiFM().favorites_getdefaultlist().stations[0].url, self.__volume)
        
        self.startmetagetter()

    def startmetagetter(self):
        self.__vlcgetmeta_enabled = True
        mediametagetter = MediaMetaGetter(self.getmeta)
        mediametagetter.infocallback.info.connect(self.updateinfo)
        self.__threadpool.start(mediametagetter)

    def playcontrol_clicked(self) -> None:
        if(Vlc().isplaying):
            self.__vlcgetmeta_enabled = False
            Vlc().stop()
            self.__btn_playcontrol.setText(None)
            self.__btn_playcontrol.setText("Play")
        else:
            Vlc().play(RaspiFM().favorites_getdefaultlist().stations[0].url, self.__volume)
            self.__btn_playcontrol.setText("Stop")
            self.startmetagetter()

    def volslider_moved(self, value:int) -> None:
       self.__volume = value
       Vlc().setvolume(self.__volume)

    def updateinfo(self, info:str):
        self.__lbl_nowplaying.setText(info)

    def getmeta(self, infocallback:pyqtSignal) -> None: 
        previnfo= ""
        sleep = 2
        while self.__vlcgetmeta_enabled:
            time.sleep(sleep)
            if(sleep < 3):
                sleep = sleep + 8
                info = Vlc().getmeta()
                if(Vlc().isplaying and info != previnfo):
                    infocallback.emit(info)
                    previnfo = info

    def resizeEvent(self, event) -> None:
        QWidget.resizeEvent(self, event)
        self.__btn_playcontrol.setMaximumWidth(self.width() - 20)

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
