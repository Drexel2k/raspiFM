import base64
import time
from types import MethodType

from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import Qt, QRunnable, QThreadPool, pyqtSlot, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QIcon, QImage, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSlider, QWidgetItem, QLayout

from ..core.RaspiFM import RaspiFM
from ..utils import utils
from..core.players.Vlc import Vlc
from .MarqueeLabel import MarqueeLabel 
from ..core.http.radiobrowserapi import stationapi
from ..core.RaspiFM import RaspiFM

class RadioWidget(QWidget):
    __slots__ = ["__vlcgetmeta_enabled", "__btn_playcontrol", "__threadpool", "__lbl_nowplaying", "__nostations"]
    __btn_playcontrol:QPushButton
    __lbl_nowplaying:MarqueeLabel
    __vlcgetmeta_enabled:bool
    __threadpool:QThreadPool
    __nostations:bool
    __inforeceived = pyqtSignal(str)

    playstarting = pyqtSignal()

    def __init__(self, startplaying:bool, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__threadpool = QThreadPool()
        self.setLayout(QVBoxLayout())

        self.__nostations = False
        self.__init(startplaying)

    def __init(self, startplaying:bool) -> None:
        defaultlist = RaspiFM().favorites_getdefaultlist()
        if(len(defaultlist.stations) > 0):
            #remove no favorites warning if warning was set before. 
            #todo: maybe add a root widget over all the info widget so that only the main or root widget has to be deleted
            #to delete also all sub widgets
            if(self.__nostations): 
                layoutitem = self.layout().takeAt(0)
                while layoutitem.count() > 0:
                    item = layoutitem.takeAt(0)
                    #QSpaceritem/QLayoutItem have no parents
                    if(isinstance(item, QWidgetItem)):
                        item.widget().close()
                        item.widget().setParent(None)

                self.__nostations = False

            station = Vlc().currentstation
            if(not station):
                station = RaspiFM().favorites_getdefaultlist().stations[0]

            if(startplaying and not Vlc().isplaying):
                if (Vlc().currentstation == None):
                    Vlc().play(station)
                else:
                    Vlc().play()                  

                if(RaspiFM().settings.touch_runontouch): #otherwise we are on dev most propably so we don't send a click on every play
                    stationapi.send_stationclicked(station.uuid)
            
            layout = self.layout()
            
            stationimagelabel = QLabel()
            layout.addWidget(stationimagelabel, alignment = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

            self.__lbl_nowplaying = MarqueeLabel()
            self.__lbl_nowplaying.setStyleSheet("QLabel { font-size:36px; }") #Font-size ist set in qt-material css and can only be overriden in css  
            layout.addWidget(self.__lbl_nowplaying, alignment=Qt.AlignmentFlag.AlignHCenter)

            layout.addStretch()

            self.__btn_playcontrol = QPushButton()
            self.__btn_playcontrol.clicked.connect(self.__playcontrol_clicked)
            self.__btn_playcontrol.setFixedSize(QSize(80, 60))
            self.__btn_playcontrol.setIconSize(QSize(80, 80))
            layout.addWidget(self.__btn_playcontrol, alignment = Qt.AlignmentFlag.AlignHCenter)

            volslider = QSlider(Qt.Orientation.Horizontal)
            volslider.sliderMoved.connect(self.__volslider_moved)
            volslider.setValue(50)
            layout.addWidget(volslider)

            qx = QPixmap()
            if(Vlc().isplaying): 
                self.__btn_playcontrol.setIcon(QIcon("src/webui/static/stop-fill-blue.svg"))
                self.__startmetagetter()
            else:
                self.__btn_playcontrol.setIcon(QIcon("src/webui/static/play-fill-blue.svg"))

            if(station.faviconb64):
                qx.loadFromData(base64.b64decode(Vlc().currentstation.faviconb64), Vlc().currentstation.faviconextension)
            else:
                renderer =  QSvgRenderer("src/webui/static/broadcast-pin-blue.svg")
                image = QImage(180, 180, QImage.Format.Format_ARGB32)
                image.fill(0x00000000)
                painter = QPainter(image)
                renderer.render(painter)
                painter.end()
                qx.convertFromImage(image)

            stationimagelabel.setPixmap(qx.scaledToHeight(180, Qt.TransformationMode.SmoothTransformation))
        else:
            self.__nostations = True
            layout = self.layout()
            layout.addStretch()
            label = QLabel("No radio station favorites found,")
            layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
            label = QLabel("go to webinterface (probably http://raspifm),")
            layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
            label = QLabel("save favorites and press refresh.")
            layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
            refreshbutton = QPushButton("Refresh")
            refreshbutton.clicked.connect(self.__refreshlicked)
            layout.addWidget(refreshbutton)
            layout.addStretch()

    def __refreshlicked(self) -> None:
        self.__init(False)

    def __playcontrol_clicked(self) -> None:
        if(Vlc().isplaying):
            self.__vlcgetmeta_enabled = False
            Vlc().stop()
            self.__btn_playcontrol.setText(None)
            self.__btn_playcontrol.setIcon(QIcon("src/webui/static/play-fill-blue.svg"))
            self.__lbl_nowplaying.setText(None)
        else:
            self.playstarting.emit()
            Vlc().play()
            self.__btn_playcontrol.setIcon(QIcon("src/webui/static/stop-fill-blue.svg"))
            self.__startmetagetter()

    def __volslider_moved(self, value:int) -> None:
       Vlc().setvolume(value)

    @pyqtSlot(str)
    def __updateinfo(self, info:str):
        self.__lbl_nowplaying.setText(info)

    def __startmetagetter(self):
        self.__vlcgetmeta_enabled = True
        mediametagetter = MediaMetaGetter(self.__getmeta)
        self.__inforeceived.connect(self.__updateinfo)
        self.__threadpool.start(mediametagetter)

    def __getmeta(self) -> None: 
        previnfo= "-1"
        sleepticks = 4
        sleeptickcount = 1
        while self.__vlcgetmeta_enabled:
            time.sleep(0.5)
            if(sleeptickcount >= sleepticks):
                if(sleepticks < 5):
                    sleepticks = 20

                sleeptickcount = 0
                info = Vlc().getmeta()
                if(Vlc().isplaying):
                    if(info != previnfo and self.__vlcgetmeta_enabled):
                        previnfo = info
                        if(utils.str_isnullorwhitespace(info)):
                            info = Vlc().currentstation.name

                        self.__inforeceived.emit(info)
  
            sleeptickcount += 1

    def resizeEvent(self, event) -> None:
        QWidget.resizeEvent(self, event)
        self.__lbl_nowplaying.setMaximumWidth(self.width() - 20)

    def closeEvent(self, event) -> None:
        self.__vlcgetmeta_enabled = False

class MediaMetaGetter(QRunnable):
    __slots__ = ["__execute"]
    __execute:MethodType

    def __init__(self, execute:MethodType):
        super().__init__()
        self.__execute = execute

    def run(self) ->None:
        self.__execute()