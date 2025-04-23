import base64
import time
from types import MethodType
#import debugpy

from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import Qt, QRunnable, QThreadPool, pyqtSlot, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QIcon, QImage, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSlider, QWidgetItem

from common import utils
from touchui.MarqueeLabel import MarqueeLabel 
from touchui.socket.RaspiFMProxy import RaspiFMProxy

class RadioWidget(QWidget):
    __slots__ = ["__vlcgetmeta_enabled", "__btn_playcontrol", "__threadpool", "__lbl_nowplaying", "__nostations"]
    __btn_playcontrol:QPushButton
    __lbl_nowplaying:MarqueeLabel
    __vlcgetmeta_enabled:bool
    __threadpool:QThreadPool
    __nostations:bool
    __inforeceived = pyqtSignal(str)

    beforeplaystarting = pyqtSignal()
    playstopped = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setLayout(QVBoxLayout())

        self.__btn_playcontrol = None
        self.__lbl_nowplaying = None
        self.__vlcgetmeta_enabled = None
        self.__threadpool = None

        self.__nostations = False

    #Added to separate public method to emit signals on radio playback init so that possible Spotify playback is stopped
    #via beforeplaystarting signal. If this would all be in __init__ signal connection can only take place after
    #playback initialization. But spotifyd can start playback before as the daemon is totally independant.
    def init_playback(self, startplaying:bool) -> None:
        station = self.__get_station()
        self.__init_controls(station)

        if not RaspiFMProxy().radio_isplaying():
            if RaspiFMProxy().radio_currentstation() is None and not station is None:
                RaspiFMProxy().radio_set_currentstation(station["uuid"])

                if startplaying:
                    self.beforeplaystarting.emit()
                    RaspiFMProxy().radio_play()

                    if RaspiFMProxy().settings_runontouch(): #Otherwise we are on dev most propably so we don't send a click on every play
                        RaspiFMProxy().radio_send_stationclicked(station["uuid"])
         
        if RaspiFMProxy().radio_isplaying(): 
            self.__btn_playcontrol.setIcon(QIcon("touchui/images/stop-fill-rpi.svg"))
            self.__startmetagetter()            

    def __init_controls(self, station):
        if station is None:
            if not self.__nostations:
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
        else:
                #Remove no favorites warning if warning was set before. 
                #Todo: maybe add a root widget over all the info widget so that only the main or root widget has to be deleted
                #to delete also all sub widgets
            if self.__nostations:
                while self.layout().count() > 0:
                    item = self.layout().takeAt(0)

                        #QSpaceritem/QLayoutItem have no parents
                    if isinstance(item, QWidgetItem):
                        item.widget().close()
                        item.widget().setParent(None)

                self.__nostations = False

            layout = self.layout()
            stationimagelabel = QLabel()
            qx = QPixmap()
            if not station["faviconb64"] is None:
                qx.loadFromData(base64.b64decode(station["faviconb64"]), station["faviconextension"])
            else:
                renderer =  QSvgRenderer("touchui/images/broadcast-pin-rpi.svg")
                image = QImage(262, 180, QImage.Format.Format_ARGB32)
                image.fill(0x00000000)
                painter = QPainter(image)
                renderer.render(painter)
                painter.end()
                qx.convertFromImage(image)

            stationimagelabel.setPixmap(qx.scaledToHeight(180, Qt.TransformationMode.SmoothTransformation))
            layout.addWidget(stationimagelabel, alignment = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

            stationnamelabel = MarqueeLabel(station["name"])
            stationnamelabel.setStyleSheet("QLabel { font-size:28px;}") #Font-size ist set in qt-material css and can only be overriden in css 
            layout.addWidget(stationnamelabel, alignment = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

            layout.insertSpacing(2, 20)

            self.__lbl_nowplaying = MarqueeLabel()
            self.__lbl_nowplaying.setStyleSheet("QLabel { font-size:36px; }") #Font-size ist set in qt-material css and can only be overriden in css  
            layout.addWidget(self.__lbl_nowplaying, alignment=Qt.AlignmentFlag.AlignHCenter)

            layout.addStretch()

            self.__btn_playcontrol = QPushButton()
            self.__btn_playcontrol.clicked.connect(self.__playcontrol_clicked)
            self.__btn_playcontrol.setFixedSize(QSize(80, 60))
            self.__btn_playcontrol.setIconSize(QSize(80, 80))
            self.__btn_playcontrol.setIcon(QIcon("touchui/images/play-fill-rpi.svg"))

            layout.addWidget(self.__btn_playcontrol, alignment = Qt.AlignmentFlag.AlignHCenter)

            volslider = QSlider(Qt.Orientation.Horizontal)
            volslider.sliderMoved.connect(self.__volslider_moved)
            volslider.setValue(RaspiFMProxy().radio_getvolume())
            layout.addWidget(volslider)

            self.__threadpool = QThreadPool()

    def __get_station(self) -> dict:
        station = station = RaspiFMProxy().radio_currentstation()

        if station == None:
            if RaspiFMProxy().settings_touch_startwith() == 1: #StartWith.LastStation
                laststation_uuid = RaspiFMProxy().settings_touch_laststation()
                if not laststation_uuid is None:
                    laststation = RaspiFMProxy().stations_getstation(laststation_uuid)
                    if not laststation is None:
                        station = laststation

            #On initial start, lastation_uuid will always be None, so try start with default list:
            #Or if last station was deleted e.g.
            if RaspiFMProxy().settings_touch_startwith() == 2 or station == None: #2 = StartWith.DefaultList 
                defaultlist = RaspiFMProxy().favorites_getdefaultlist()
                if len(defaultlist["stations"]) > 0:
                        station = defaultlist["stations"][0]["radiostation"]

            #If station is still None, check for check if there is any station in favorites and
            #take the first:
            if station == None:
                station = RaspiFMProxy().favorites_get_any_station()["radiostation"]

        return station

    def __refreshlicked(self) -> None:
        self.init_playback(False)

    def __playcontrol_clicked(self) -> None:
        if RaspiFMProxy().radio_isplaying():
            self.__vlcgetmeta_enabled = False
            RaspiFMProxy().radio_stop()
            self.__btn_playcontrol.setText(None)
            self.__btn_playcontrol.setIcon(QIcon("touchui/images/play-fill-rpi.svg"))
            self.__lbl_nowplaying.setText(None)
            self.playstopped.emit()
        else:
            self.beforeplaystarting.emit()
            RaspiFMProxy().radio_play()
            self.__btn_playcontrol.setIcon(QIcon("touchui/images/stop-fill-rpi.svg"))
            self.__startmetagetter()

    def __volslider_moved(self, value:int) -> None:
       RaspiFMProxy().radio_setvolume(value)

    @pyqtSlot(str)
    def __updateinfo(self, info:str):
        self.__lbl_nowplaying.setText(info)

    def __startmetagetter(self):
        self.__vlcgetmeta_enabled = True
        mediametagetter = MediaMetaGetter(self.__getmeta)
        self.__inforeceived.connect(self.__updateinfo)
        self.__threadpool.start(mediametagetter)
    
    def __getmeta(self) -> None:
        #To debug remove comment on next line and in import statement for debugpy at beginning of file
        #debugpy.debug_this_thread()
        previnfo= "-1"

        #Split the sleep phase into 0.5 seconds that closing the app is more responsive e.g.
        sleeptickslimit = 4
        sleeptickcount = 1
        while self.__vlcgetmeta_enabled:
            time.sleep(0.5)
            if sleeptickcount >= sleeptickslimit:
                #First sleep phase is shorter than next spleep phases, so that first info is coming faster
                if sleeptickslimit < 5:
                    sleeptickslimit = 20

                sleeptickcount = 0
                info = RaspiFMProxy().radio_getmeta()
                if RaspiFMProxy().radio_isplaying():
                    if info != previnfo and self.__vlcgetmeta_enabled:
                        previnfo = info
                        if utils.str_isnullorwhitespace(info):
                            info = RaspiFMProxy().radio_currentstation()["name"]

                        self.__inforeceived.emit(info)
  
            sleeptickcount += 1

    def resizeEvent(self, event) -> None:
        QWidget.resizeEvent(self, event)

        #Is null if no stations are configured yet.
        if not self.__lbl_nowplaying is None:
            self.__lbl_nowplaying.setMaximumWidth(self.width() - 20)

    def closeEvent(self, event) -> None:
        self.__vlcgetmeta_enabled = False

class MediaMetaGetter(QRunnable):
    __slots__ = ["__execute"]
    __execute:MethodType

    def __init__(self, execute:MethodType):
        super().__init__()
        self.__execute = execute

    def run(self) -> None:
        self.__execute()