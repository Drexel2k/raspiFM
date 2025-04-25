import os

from PyQt6 import QtDBus, QtCore
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QVBoxLayout,QHBoxLayout, QWidget, QMainWindow, QSizePolicy, QScrollArea, QWidgetItem

from touchui.FavoritesWidget import FavoritesWidget
from touchui.RadioWidget import RadioWidget
from touchui.SpotifyWidget import SpotifyWidget
from touchui.SettingsWidget import SettingsWidget
from touchui.PushButtonMain import PushButtonMain
from touchui.socket.RaspiFMProxy import RaspiFMProxy

class MainWindow(QMainWindow):
    __slots__ = ["__mainwidget", "__spotify_dbusname", "__system_dbusconnection", "__radiobutton", "__favoritesbutton", "__spotifybutton", "__settingsbutton", "__activebutton", "__activebackgroundcolor"]
    __mainwidget:QWidget
    __spotify_dbusname:str
    __system_dbusconnection:QtDBus.QDBusConnection

    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("raspiFM touch")
        scroll = QScrollArea()
        
        self.__mainwidget = QWidget()
        self.__mainwidget.setLayout(QHBoxLayout())

        scroll.setWidget(self.__mainwidget)
        self.setCentralWidget(scroll)

        RaspiFMProxy()

        self.__spotify_dbusname = None
        self.__system_dbusconnection = None

        #Create background color from qt-material primary color
        hexColor = os.environ["QTMATERIAL_PRIMARYCOLOR"][1:]
        self.__activebackgroundcolor = "rgba("
        for i in (0, 2, 4):
            self.__activebackgroundcolor += str(int(hexColor[i:i+2], 16)) +", "

        self.__activebackgroundcolor += "0.2)"

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

        if RaspiFMProxy().spotify_isplaying():
            self.__change_icons_spotify_playing()
            self.__spotifybutton.setStyleSheet(f'QPushButton {{ background-color: { self.__activebackgroundcolor }; }}')
            self.__activebutton = self.__spotifybutton

            self.__mainwidget.layout().addWidget(SpotifyWidget(), stretch=4)            
        else:
            self.__activebutton = self.__radiobutton

            radiowidget = RadioWidget()
            radiowidget.beforeplaystarting.connect(self.__radio_starts_playing)
            radiowidget.playstopped.connect(self.__change_icon_radio_stopped)

            radiowidget.init_playback(True)

            #Can not be playing if no stations are available on initial start e.g.
            if RaspiFMProxy().radio_isplaying():
                self.__radiobutton.setIcon(QIcon("touchui/images/broadcast-pin-music-rpi.svg"))
            else:
                self.__radiobutton.setIcon(QIcon("touchui/images/broadcast-pin-rpi.svg"))

            self.__spotifybutton.setIcon(QIcon("touchui/images/spotify-rpi.svg"))
            self.__radiobutton.setStyleSheet(f'QPushButton {{ background-color: { self.__activebackgroundcolor }; }}')

            self.__mainwidget.layout().addWidget(radiowidget, stretch=4) 
    
    def __radio_starts_playing(self) -> None:
        self.__stopspotify()
        #Spotify Icon is changed on Spotify stopped playing DBus message
        self.__change_icon_radio_playing()

    def __stopspotify(self) -> None:
        interface = QtDBus.QDBusInterface(self.__spotify_dbusname, dbusstrings.spotifydpath, dbusstrings.spotifydinterface, self.__system_dbusconnection)
        interface.call(dbusstrings.spotifydmethodpause)

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
            spotifywdidget = SpotifyWidget()
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
        self.__mainwidget.setFixedSize(self.width(), self.height())

    def closeEvent(self, event) -> None:
        QMainWindow.closeEvent(self, event)
        widget = self.__mainwidget.layout().itemAt(1).widget()
        widget.close()
        widget.setParent(None)
        RaspiFMProxy().raspifm_shutdown()