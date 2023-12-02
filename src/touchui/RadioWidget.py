import base64
import time
from types import MethodType

from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import (Qt, QRunnable, QThreadPool, Slot, Signal, QSize)
from PySide6.QtGui import (QPixmap, QIcon, QImage, QPainter)
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QSlider)

from..core.Vlc import Vlc
from .MarqueeLabel import MarqueeLabel

class RadioWidget(QWidget):
    __slots__ = ["__vlcgetmeta_enabled", "__btn_playcontrol", "__threadpool", "__lbl_nowplaying"]
    __btn_playcontrol:QPushButton
    __lbl_nowplaying:MarqueeLabel
    __vlcgetmeta_enabled:bool
    __threadpool:QThreadPool
    
    __inforeceived = Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if(Vlc().currentstation):
            self.__threadpool = QThreadPool()
            
            main_layout_vertical = QVBoxLayout()
            self.setLayout(main_layout_vertical)
    
            stationimagelabel = QLabel()
            qx = QPixmap()
            if(Vlc().currentstation.faviconb64):
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
            main_layout_vertical.addWidget(stationimagelabel, alignment = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

            self.__lbl_nowplaying = MarqueeLabel()
            self.__lbl_nowplaying.setStyleSheet("QLabel { font-size:36px; }") #Font-size ist set in qt-material css and can only be overriden in css  
            main_layout_vertical.addWidget(self.__lbl_nowplaying, alignment=Qt.AlignmentFlag.AlignHCenter)

            main_layout_vertical.addStretch()

            self.__btn_playcontrol = QPushButton()
            self.__btn_playcontrol.clicked.connect(self.playcontrol_clicked)
            self.__btn_playcontrol.setIcon(QIcon("src/webui/static/stop-fill-blue.svg"))
            self.__btn_playcontrol.setFixedSize(QSize(80, 60))
            self.__btn_playcontrol.setIconSize(QSize(80, 80))
            main_layout_vertical.addWidget(self.__btn_playcontrol, alignment = Qt.AlignmentFlag.AlignHCenter)

            volslider = QSlider(Qt.Orientation.Horizontal)
            volslider.sliderMoved.connect(self.volslider_moved)
            volslider.setValue(50)
            main_layout_vertical.addWidget(volslider)

            if(not Vlc().isplaying):
                Vlc().play(Vlc().currentstation.url)
            
            self.startmetagetter()

    def playcontrol_clicked(self) -> None:
        if(Vlc().isplaying):
            self.__vlcgetmeta_enabled = False
            Vlc().stop()
            self.__btn_playcontrol.setText(None)
            self.__btn_playcontrol.setIcon(QIcon("src/webui/static/play-fill-blue.svg"))
            self.__lbl_nowplaying.setText(None)
        else:
            Vlc().play()
            self.__btn_playcontrol.setIcon(QIcon("src/webui/static/stop-fill-blue.svg"))
            self.startmetagetter()

    def volslider_moved(self, value:int) -> None:
       Vlc().setvolume(value)

    @Slot(str)
    def updateinfo(self, info:str):
        self.__lbl_nowplaying.setText(info)

    def startmetagetter(self):
        self.__vlcgetmeta_enabled = True
        mediametagetter = MediaMetaGetter(self.getmeta)
        self.__inforeceived.connect(self.updateinfo)
        self.__threadpool.start(mediametagetter)

    def getmeta(self) -> None: 
        previnfo= ""
        sleepticks = 4
        sleeptickcount = 1
        while self.__vlcgetmeta_enabled:
            time.sleep(0.5)
            if(sleeptickcount >= sleepticks):
                if(sleepticks < 5):
                    sleepticks = 20

                sleeptickcount = 0
                info = Vlc().getmeta()
                if(Vlc().isplaying and info != previnfo and self.__vlcgetmeta_enabled):
                    self.__inforeceived.emit(info)
                    previnfo = info
            
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