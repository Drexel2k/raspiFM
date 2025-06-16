import os
import subprocess
from subprocess import Popen
import traceback

from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QVBoxLayout,QHBoxLayout, QWidget, QMainWindow, QSizePolicy, QScrollArea, QWidgetItem, QLabel, QPushButton

from common import socketstrings
from touchui.FavoritesWidget import FavoritesWidget
from touchui.RadioWidget import RadioWidget
from touchui.SpotifyWidget import SpotifyWidget
from touchui.SettingsWidget import SettingsWidget
from touchui.PushButtonMain import PushButtonMain
from touchui.socket.RaspiFMQtProxy import RaspiFMQtProxy

class MainWindow(QMainWindow):
    __slots__ = ["__mainwidget", "__radiobutton", "__favoritesbutton", "__spotifybutton", "__settingsbutton", "__activebutton", "__activebackgroundcolor", "__spotify_playing", "__raspifm_service_not_available_controls_set"]
    __mainwidget:QWidget
    __radiobutton:QPushButton
    __favoritesbutton:QPushButton
    __spotifybutton:QPushButton
    __settingsbutton:QPushButton
    __activebutton:QPushButton
    __activebackgroundcolor:str
    __spotify_playing:bool
    __raspifm_service_not_available_controls_set:bool

    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #print("Qt: v", QtCore.QT_VERSION_STR, "\tPyQt: v", QtCore.PYQT_VERSION_STR)

        #otherwise resize event which accesses __mainwidget will fail
        self.__mainwidget = None
        self.resize(800, 480)   

        self.setWindowTitle("raspiFM touch")
        scroll = QScrollArea()
        scroll.setStyleSheet("QScrollBar:vertical { width: 15px; } QScrollBar:horizontal { height: 15px; }")
        
        self.__mainwidget = QWidget()
        self.__mainwidget.setLayout(QHBoxLayout())

        #Create background color from qt-material primary color
        hexColor = os.environ["QTMATERIAL_PRIMARYCOLOR"][1:]
        self.__activebackgroundcolor = "rgba("
        for i in (0, 2, 4):
            self.__activebackgroundcolor += str(int(hexColor[i:i+2], 16)) +", "

        self.__activebackgroundcolor += "0.2)"

        self.__spotify_playing = False
        self.__raspifm_service_not_available_controls_set = False

        scroll.setWidget(self.__mainwidget)
        self.setCentralWidget(scroll)

        self.__init_controls()

    def __init_controls(self) -> None:
        try:
            RaspiFMQtProxy()
        except (ConnectionRefusedError, FileNotFoundError):
            traceback.print_exc()
            if not self.__raspifm_service_not_available_controls_set:
                self.__raspifm_service_not_available_controls_set = True
                info_layout_vertical = QVBoxLayout()
                self.__mainwidget.layout().addLayout(info_layout_vertical)
                info_layout_vertical.addStretch()
                label = QLabel("RaspiFM service not running,")
                info_layout_vertical.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
                label = QLabel("run the service (more info in the docs directory),")
                info_layout_vertical.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
                label = QLabel("and press refresh.")
                info_layout_vertical.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
                refreshbutton = QPushButton("Refresh")
                refreshbutton.clicked.connect(self.__refreshlicked)
                info_layout_vertical.addWidget(refreshbutton)
                info_layout_vertical.addStretch()

            return
        
        if RaspiFMQtProxy().settings_runontouch():
            self.showFullScreen()
            self.setCursor(Qt.CursorShape.BlankCursor)  
        
        if self.__raspifm_service_not_available_controls_set:
            #info_layout_vertical QVBoxLayout
            layout = self.__mainwidget.layout().takeAt(0)
            while layout.count() > 0:
                item = layout.takeAt(0)

                #QSpaceritem/QLayoutItem have no parents
                if isinstance(item, QWidgetItem):
                    item.widget().close()
                    item.widget().setParent(None)     

            self.__mainwidget.layout().removeItem(layout)       
            self.__raspifm_service_not_available_controls_set = False

        RaspiFMQtProxy().core_notification_available.connect(self.__core_notification_available)

        left_layout_vertical = QVBoxLayout()
        self.__mainwidget.layout().addLayout(left_layout_vertical, stretch=1)
    
        self.__radiobutton = PushButtonMain()
        self.__radiobutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding) 
        self.__radiobutton.clicked.connect(self.__radioclicked)

        self.__favoritesbutton = PushButtonMain()
        self.__favoritesbutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        #Size of icon is set PushButtonMain class!!!
        self.__favoritesbutton.setIcon(QIcon("touchui/images/star-rpi.svg"))
        self.__favoritesbutton.clicked.connect(self.__favoritesclicked)

        self.__spotifybutton = PushButtonMain()
        self.__spotifybutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.__spotifybutton.clicked.connect(self.__spotifyclicked)

        self.__settingsbutton = PushButtonMain()
        self.__settingsbutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.__settingsbutton.setIcon(QIcon("touchui/images/gear-rpi.svg"))
        self.__settingsbutton.clicked.connect(self.__settingsclicked)

        left_layout_vertical.addWidget(self.__radiobutton)
        left_layout_vertical.addWidget(self.__favoritesbutton)
        left_layout_vertical.addWidget(self.__spotifybutton)
        left_layout_vertical.addWidget(self.__settingsbutton)

        if RaspiFMQtProxy().spotify_isplaying():
            self.__spotify_playing = True
            self.__change_icons_spotify_playing()
            self.__spotifybutton.setStyleSheet(f'QPushButton {{ background-color: { self.__activebackgroundcolor }; }}')
            self.__activebutton = self.__spotifybutton

            self.__mainwidget.layout().addWidget(SpotifyWidget(RaspiFMQtProxy().spotify_currently_playing()), stretch=4)            
        else:
            self.__activebutton = self.__radiobutton

            radiowidget = RadioWidget()
            radiowidget.beforeplaystarting.connect(self.__radio_starts_playing)
            radiowidget.playstopped.connect(self.__change_icon_radio_stopped)

            radiowidget.init_playback(True)

            #Can not be playing if no stations are available on initial start e.g.
            if RaspiFMQtProxy().radio_isplaying():
                self.__radiobutton.setIcon(QIcon("touchui/images/broadcast-pin-music-rpi.svg"))
            else:
                self.__radiobutton.setIcon(QIcon("touchui/images/broadcast-pin-rpi.svg"))

            self.__spotifybutton.setIcon(QIcon("touchui/images/spotify-rpi.svg"))
            self.__radiobutton.setStyleSheet(f'QPushButton {{ background-color: { self.__activebackgroundcolor }; }}')

            self.__mainwidget.layout().addWidget(radiowidget, stretch=4) 
        
        RaspiFMQtProxy().players_status_subscribe()

    def __refreshlicked(self) -> None:
        self.__init_controls()

    def __core_notification_available(self, notification:dict):
        if notification[socketstrings.message_string] == "radio_change":
            if isinstance(self.__mainwidget.layout().itemAt(1).widget(), RadioWidget):
                self.__mainwidget.layout().itemAt(1).widget().radio_update(notification[socketstrings.args_string]["radio_currentplaying"])
        
        if notification[socketstrings.message_string] == "spotify_change":
            #Spotify stopped playing
            if notification[socketstrings.args_string]["spotify_currently_playing"] is None:
                self.__spotify_playing = False
                self.__change_icons_spotify_stopped()
                if isinstance(self.__mainwidget.layout().itemAt(1).widget(), SpotifyWidget):
                    self.__mainwidget.layout().itemAt(1).widget().spotify_update(None)
            else:
                spotify_wasplaying = self.__spotify_playing
                self.__spotify_playing = True
                self.__change_icons_spotify_playing()

                #If spotify widget is active simply update the information.
                if isinstance(self.__mainwidget.layout().itemAt(1).widget(), SpotifyWidget):
                    self.__mainwidget.layout().itemAt(1).widget().spotify_update(notification[socketstrings.args_string]["spotify_currently_playing"])
                else:
                    #If spotify playback was jsut startet switch to spotify widget. If Spotify was already playing
                    #the user switched manually to another widget before, so leave this widget as it is.
                    if not spotify_wasplaying:
                        self.__activebutton.setStyleSheet("QPushButton { background-color: transparent; }")
                        self.__spotifybutton.setStyleSheet(f'QPushButton {{ background-color: { self.__activebackgroundcolor }; }}')
                        self.__activebutton = self.__spotifybutton
                        spotifywidget = SpotifyWidget(notification[socketstrings.args_string]["spotify_currently_playing"])
                        spotifywidget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                        widgetitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), spotifywidget)
                        self.__closewidgetitem(widgetitem)                    

    def __radio_starts_playing(self) -> None:
        RaspiFMQtProxy().spotify_stop()
        #Spotify icon is changed on Spotify stopped playing DBus message
        self.__change_icon_radio_playing()

    def __radioclicked(self) -> None:
        self.__activebutton.setStyleSheet("QPushButton { background-color: transparent; }")
        self.__radiobutton.setStyleSheet(f'QPushButton {{ background-color: { self.__activebackgroundcolor }; }}')
        self.__activebutton = self.__radiobutton
        if not isinstance(self.__mainwidget.layout().itemAt(1).widget(), RadioWidget):
            radiowidget = RadioWidget()
            radiowidget.init_playback(False)
            radiowidget.beforeplaystarting.connect(self.__radio_starts_playing)
            radiowidget.playstopped.connect(self.__change_icon_radio_stopped)

            radiowidget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

            widgetitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), radiowidget)
            self.__closewidgetitem(widgetitem)

    def __favoritelicked(self) -> None:
        self.__radio_starts_playing()
        self.__activebutton.setStyleSheet("QPushButton { background-color: transparent; }")
        self.__radiobutton.setStyleSheet(f'QPushButton {{ background-color: { self.__activebackgroundcolor }; }}')
        self.__activebutton = self.__radiobutton

        radiowidget = RadioWidget()
        radiowidget.init_playback(True)
        radiowidget.beforeplaystarting.connect(self.__radio_starts_playing)
        radiowidget.playstopped.connect(self.__change_icon_radio_stopped)

        radiowidget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        widgetitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), radiowidget)
        self.__closewidgetitem(widgetitem)

    def __favoritesclicked(self) -> None:
        self.__activebutton.setStyleSheet("QPushButton { background-color: transparent; }")
        self.__favoritesbutton.setStyleSheet(f'QPushButton {{ background-color: { self.__activebackgroundcolor }; }}')
        self.__activebutton = self.__favoritesbutton
        if not isinstance(self.__mainwidget.layout().itemAt(1).widget(), FavoritesWidget):
            favoriteswdidget = FavoritesWidget()
            favoriteswdidget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            favoriteswdidget.favclicked.connect(self.__favoritelicked)
            widgetitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), favoriteswdidget)
            self.__closewidgetitem(widgetitem)

    def __spotifyclicked(self) -> None:
        self.__activebutton.setStyleSheet("QPushButton { background-color: transparent; }")
        self.__spotifybutton.setStyleSheet(f'QPushButton {{ background-color: { self.__activebackgroundcolor }; }}')
        self.__activebutton = self.__spotifybutton
        if not isinstance(self.__mainwidget.layout().itemAt(1).widget(), SpotifyWidget):
            spotifywdidget = SpotifyWidget(RaspiFMQtProxy().spotify_currently_playing())
            spotifywdidget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            widgetitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), spotifywdidget)
            self.__closewidgetitem(widgetitem)

    def __settingsclicked(self) -> None:
        self.__activebutton.setStyleSheet("QPushButton { background-color: transparent; }")
        self.__settingsbutton.setStyleSheet(f'QPushButton {{ background-color: { self.__activebackgroundcolor }; }}')
        self.__activebutton = self.__settingsbutton
        if not isinstance(self.__mainwidget.layout().itemAt(1).widget(), SettingsWidget):
            settingswdiget = SettingsWidget()
            settingswdiget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            widgetitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), settingswdiget)
            self.__closewidgetitem(widgetitem)
    
    def __change_icons_spotify_playing(self) -> None:
        self.__radiobutton.setIcon(QIcon("touchui/images/broadcast-pin-rpi.svg"))
        self.__spotifybutton.setIcon(QIcon("touchui/images/spotify-music-rpi.svg"))
    
    def __change_icons_spotify_stopped(self) -> None:
        self.__spotifybutton.setIcon(QIcon("touchui/images/spotify-rpi.svg"))

    def __change_icon_radio_playing(self) -> None:
        self.__radiobutton.setIcon(QIcon("touchui/images/broadcast-pin-music-rpi.svg"))

    def __change_icon_radio_stopped(self) -> None:
        self.__radiobutton.setIcon(QIcon("touchui/images/broadcast-pin-rpi.svg"))

    def __closewidgetitem(self, widgetitem:QWidgetItem) -> None:
        widget = widgetitem.widget()

        if isinstance(widget, RadioWidget):
            widget.beforeplaystarting.disconnect()

        if isinstance(widget, FavoritesWidget):
            widget.favclicked.disconnect()

        widget.close()
        widget.setParent(None)

    def keyPressEvent(self, event): 
        if event.key() == QtCore.Qt.Key.Key_Escape:
            if self.isFullScreen():
                self.showNormal() 
            else:
                self.showFullScreen()
    
    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)
        if not self.__mainwidget is None:
            self.__mainwidget.setFixedSize(self.width(), self.height())

    def closeEvent(self, event) -> None:
        #Closing the ui shall also shutdown all processes but nginx which is a system daemon, we don't have rights to shut it down
        if not self.__raspifm_service_not_available_controls_set:
            QMainWindow.closeEvent(self, event)
            widget = self.__mainwidget.layout().itemAt(1).widget()
            widget.close()
            widget.setParent(None)
            RaspiFMQtProxy().raspifm_shutdown()

        ps_process = Popen(["ps", "-aux"], stdout=subprocess.PIPE, text=True)
        prgrep_process = Popen(["grep", "-i", "gunicorn: master"], stdin=ps_process.stdout, stdout=subprocess.PIPE, text=True)
        processes_matched = prgrep_process.communicate()[0]
        process_matched_info = None

        process_ids_to_end =[]
        for process_matched in processes_matched.splitlines():
            process_matched_info = process_matched.split(maxsplit=10)
            if not "grep" in process_matched_info[10].lower():
                process_ids_to_end.append(process_matched_info[1])
        
        ps_process = Popen(["ps", "-aux"], stdout=subprocess.PIPE, text=True)
        prgrep_process = Popen(["grep", "-i", "spotifyd"], stdin=ps_process.stdout, stdout=subprocess.PIPE, text=True)
        processes_matched = prgrep_process.communicate()[0]

        for process_matched in processes_matched.splitlines():
            process_matched_info = process_matched.split(maxsplit=10)
            if not "grep" in process_matched_info[10].lower():
                process_ids_to_end.append(process_matched_info[1])

        for process_id in process_ids_to_end:
            subprocess.run(["kill", "-SIGTERM", process_id])