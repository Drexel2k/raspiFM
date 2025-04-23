import os

from PyQt6 import QtDBus, QtCore
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QVBoxLayout,QHBoxLayout, QWidget, QMainWindow, QSizePolicy, QScrollArea, QWidgetItem

from core.players.SpotifyInfo import SpotifyInfo
from common import utils
from touchui.FavoritesWidget import FavoritesWidget
from touchui.RadioWidget import RadioWidget
from touchui.SpotifyWidget import SpotifyWidget
from touchui.SettingsWidget import SettingsWidget
from touchui.PushButtonMain import PushButtonMain
from touchui import dbusstrings
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
        self.__initializespotify()

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
        
    def __initializespotify(self) -> None:
        self.__system_dbusconnection = QtDBus.QDBusConnection.systemBus()
        self.__system_dbusconnection.registerObject('/', self) #needed to prevent hang of connect call, is a bug, which will be fixed.
        
        #check if spotify is already up
        servicenames = self.__system_dbusconnection.interface().registeredServiceNames().value()
        for name in servicenames:
            if name.startswith(dbusstrings.spotifydservicestart):
               self.__spotify_dbusname = name
               break
        
        if utils.str_isnullorwhitespace(self.__spotify_dbusname):
            #if spotify is not up, listen for it to come up
            self.__system_dbusconnection.connect(dbusstrings.dbusservice, dbusstrings.dbuspath, dbusstrings.dbusinterface, dbusstrings.dbussignalnameownerchanged, self.__dbus_nameownerchanged)
        else:
            #if spotify is up, listen to player/track changes
            self.__system_dbusconnection.connect(self.__spotify_dbusname, dbusstrings.spotifydpath, dbusstrings.dbuspropertiesinterface, dbusstrings.dbussignalpropertieschanged, self.__spotifyd_propertieschanged)

            interface = QtDBus.QDBusInterface(self.__spotify_dbusname, dbusstrings.spotifydpath, dbusstrings.dbuspropertiesinterface, self.__system_dbusconnection)
            message = interface.call(dbusstrings.dbusmethodget, dbusstrings.spotifydinterface, dbusstrings.spotifydpropertyplaybackstatus)
            state = message.arguments()[0]
            if state == "Playing":
                message = interface.call(dbusstrings.dbusmethodget, dbusstrings.spotifydinterface, dbusstrings.spotifydpropertymetadata)
                metadata = message.arguments()[0]
                RaspiFM().spotify_set_currentplaying(SpotifyInfo(metadata[dbusstrings.spotifydmetadatatitle], metadata[dbusstrings.spotifydmetadataalbum], metadata[dbusstrings.spotifydmetadataartists], metadata[dbusstrings.spotifydmetadataarturl]))

    @pyqtSlot(QtDBus.QDBusMessage)
    def __dbus_nameownerchanged(self, msg:QtDBus.QDBusMessage) -> None:
        args = msg.arguments()
        servicename = args[0]
        newowner = args[1]
        oldowner = args[2]

        if servicename.startswith("org.mpris.MediaPlayer2.spotifyd.instance"):
            #service new on the bus
            if utils.str_isnullorwhitespace(newowner):
                self.__system_dbusconnection.disconnect(dbusstrings.dbusservice, dbusstrings.dbuspath, dbusstrings.dbusinterface, dbusstrings.dbussignalnameownerchanged, self.__dbus_nameownerchanged)
                self.__spotify_dbusname = servicename
                self.__system_dbusconnection.connect(self.__spotify_dbusname, dbusstrings.spotifydpath, dbusstrings.dbuspropertiesinterface, dbusstrings.dbussignalpropertieschanged, self.__spotifyd_propertieschanged)

            #service left bus
            if utils.str_isnullorwhitespace(oldowner):
                self.__spotify_dbusname = None
                self.__system_dbusconnection.connect(dbusstrings.dbusservice, dbusstrings.dbuspath, dbusstrings.dbusinterface, dbusstrings.dbussignalnameownerchanged, self.__dbus_nameownerchanged)
                self.__spotifystopped()

    @pyqtSlot(QtDBus.QDBusMessage)
    def __spotifyd_propertieschanged(self, msg:QtDBus.QDBusMessage) -> None:
        changeproperties = msg.arguments()[1]

        #Sometimes, not reproducable, not alle infos are in the changeproperties, onyl one attribute like volume is in it.
        #Normaly after that another propertieschange signal comes in with the full infos.
        if not dbusstrings.spotifydpropertymetadata in changeproperties or not dbusstrings.spotifydpropertyplaybackstatus in changeproperties:
            return
            #interface = QtDBus.QDBusInterface(self.__spotify_dbusname, dbusstrings.spotifydpath, dbusstrings.dbuspropertiesinterface, self.__system_dbusconnection)
            #msg = interface.call(dbusstrings.dbusmethodgetall, dbusstrings.spotifydinterface)
            #changeproperties = msg.arguments()[0]

        metadata = changeproperties[dbusstrings.spotifydpropertymetadata]
        spotify_wasplaying = RaspiFM().spotify_isplaying()
        RaspiFM().spotify_set_currentplaying(SpotifyInfo(metadata[dbusstrings.spotifydmetadatatitle], metadata[dbusstrings.spotifydmetadataalbum], metadata[dbusstrings.spotifydmetadataartists], metadata[dbusstrings.spotifydmetadataarturl]))
        
        if changeproperties[dbusstrings.spotifydpropertyplaybackstatus] == "Playing":
            RaspiFM().radio_stop()

            self.__change_icons_spotify_playing()

            #If spotify widget is active simply update the information.
            if isinstance(self.__mainwidget.layout().itemAt(1).widget(), SpotifyWidget):
                self.__mainwidget.layout().itemAt(1).widget().spotifyupdate()
            else:
                #If spotify playback was jsut startet switch to spotify widget. If Spotify was already playing
                #the user switched manually to another widget before, so leave this widget as it is.
                if not spotify_wasplaying:
                    self.__activebutton.setStyleSheet("QPushButton { background-color: transparent; }")
                    self.__spotifybutton.setStyleSheet(f'QPushButton {{ background-color: { self.__activebackgroundcolor }; }}')
                    self.__activebutton = self.__spotifybutton
                    spotifywidget = SpotifyWidget()
                    spotifywidget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                    widgetitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), spotifywidget)
                    self.__closewidgetitem(widgetitem)

        else:
            if RaspiFM().spotify_isplaying():
                #Not only triggered when Spotify stopped via app, but also when radio
                #was manually started again, so this is no sign of nothing is playing!
                self.__spotifybutton.setIcon(QIcon("touchui/images/spotify-rpi.svg"))
                RaspiFM().spotify_set_isplaying(False)

                if isinstance(self.__mainwidget.layout().itemAt(1).widget(), SpotifyWidget):
                    self.__mainwidget.layout().itemAt(1).widget().spotifyupdate()   
    
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
        RaspiFM().radio_shutdown()