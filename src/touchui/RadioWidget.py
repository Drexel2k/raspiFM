import base64
#import debugpy

from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import Qt, QRunnable, QThreadPool, pyqtSlot, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QIcon, QImage, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSlider, QWidgetItem

from touchui.MarqueeLabel import MarqueeLabel 
from touchui.socket.RaspiFMQtProxy import RaspiFMQtProxy

class RadioWidget(QWidget):
    __slots__ = ["__btn_playcontrol", "__lbl_nowplaying", "__nostations"]
    __btn_playcontrol:QPushButton
    __lbl_nowplaying:MarqueeLabel
    __nostations:bool

    beforeplaystarting = pyqtSignal()
    playstopped = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setLayout(QVBoxLayout())

        self.__btn_playcontrol = None
        self.__lbl_nowplaying = None

        self.__nostations = False

    #Added to separate public method to emit signals on radio playback init so that possible Spotify playback is stopped
    #via beforeplaystarting signal. If this would all be in __init__ signal connection can only take place after
    #playback initialization. But spotifyd can start playback before as the daemon is totally independant.
    def init_playback(self, startplaying:bool) -> None:
        station = None
        if RaspiFMQtProxy().radio_isplaying():
            station = RaspiFMQtProxy().radio_get_currentstation()
        else:
            station = self.__get_station()

        self.__init_controls(station)

        if not RaspiFMQtProxy().radio_isplaying():
            if not station is None:
                RaspiFMQtProxy().radio_set_currentstation(station["uuid"])

                if startplaying:
                    self.beforeplaystarting.emit()
                    RaspiFMQtProxy().radio_play()
         
        if RaspiFMQtProxy().radio_isplaying():
            self.radio_update(RaspiFMQtProxy().radio_getmeta())
            self.__btn_playcontrol.setIcon(QIcon("touchui/images/stop-fill-rpi.svg"))

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
            volslider.setValue(RaspiFMQtProxy().radio_getvolume())
            layout.addWidget(volslider)

    def __get_station(self) -> dict:
        station = station = RaspiFMQtProxy().radio_get_currentstation()

        if station == None:
            if RaspiFMQtProxy().settings_touch_startwith() == 1: #StartWith.LastStation
                laststation_uuid = RaspiFMQtProxy().settings_touch_laststation()
                if not laststation_uuid is None:
                    laststation = RaspiFMQtProxy().stations_getstation(laststation_uuid)
                    if not laststation is None:
                        station = laststation

            #On initial start, lastation_uuid will always be None, so try start with default list:
            #Or if last station was deleted e.g.
            if RaspiFMQtProxy().settings_touch_startwith() == 2 or station == None: #2 = StartWith.DefaultList 
                defaultlist = RaspiFMQtProxy().favorites_getdefaultlist()
                if len(defaultlist["stations"]) > 0:
                        station = defaultlist["stations"][0]["radiostation"]

            #If station is still None, check for check if there is any station in favorites and
            #take the first:
            if station == None:
                station = RaspiFMQtProxy().favorites_get_any_station()["radiostation"]

        return station

    def __refreshlicked(self) -> None:
        self.init_playback(False)

    def __playcontrol_clicked(self) -> None:
        if RaspiFMQtProxy().radio_isplaying():
            RaspiFMQtProxy().radio_stop()
            self.__btn_playcontrol.setText(None)
            self.__btn_playcontrol.setIcon(QIcon("touchui/images/play-fill-rpi.svg"))
            self.__lbl_nowplaying.setText(None)
            self.playstopped.emit()
        else:
            self.beforeplaystarting.emit()
            RaspiFMQtProxy().radio_play()
            self.__btn_playcontrol.setIcon(QIcon("touchui/images/stop-fill-rpi.svg"))

    def __volslider_moved(self, value:int) -> None:
       RaspiFMQtProxy().radio_setvolume(value)

    def radio_update(self, info:str):
        self.__lbl_nowplaying.setText(info)

    def resizeEvent(self, event) -> None:
        QWidget.resizeEvent(self, event)

        #Is null if no stations are configured yet.
        if not self.__lbl_nowplaying is None:
            self.__lbl_nowplaying.setMaximumWidth(self.width() - 20)