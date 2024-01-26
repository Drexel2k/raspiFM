from PyQt6 import QtDBus, QtCore
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QVBoxLayout,QHBoxLayout, QWidget, QMainWindow, QSizePolicy, QScrollArea, QWidgetItem

from core.RaspiFM import RaspiFM
from core.players.SpotifyInfo import SpotifyInfo
from utils import utils
from touchui.FavoritesWidget import FavoritesWidget
from touchui.RadioWidget import RadioWidget
from touchui.SpotifyWidget import SpotifyWidget
from touchui.SettingsWidget import SettingsWidget
from touchui.PushButtonMain import PushButtonMain
from touchui import dbusstrings

class MainWindow(QMainWindow):
    __slots__ = ["__mainwidget", "__spotify_dbusname", "__system_dbusconnection"]
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

        self.__spotify_dbusname = None
        self.__system_dbusconnection = None

        self.__initializespotify()

        left_layout_vertical = QVBoxLayout()
        self.__mainwidget.layout().addLayout(left_layout_vertical, stretch=1)
    
        radiobutton = PushButtonMain()
        radiobutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding) 
        radiobutton.setIcon(QIcon("touchui/images/broadcast-pin-blue.svg"))
        radiobutton.clicked.connect(self.__radioclicked)

        favoritesbutton = PushButtonMain()
        favoritesbutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        favoritesbutton.setIcon(QIcon("touchui/images/star-blue.svg"))
        favoritesbutton.clicked.connect(self.__favoritesclicked)

        spotifybutton = PushButtonMain()
        spotifybutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        spotifybutton.setIcon(QIcon("touchui/images/spotify-blue.svg"))
        spotifybutton.clicked.connect(self.__spotifyclicked)

        settingsbutton = PushButtonMain()
        settingsbutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        settingsbutton.setIcon(QIcon("touchui/images/gear-blue.svg"))
        settingsbutton.clicked.connect(self.__settingsclicked)

        left_layout_vertical.addWidget(radiobutton)
        left_layout_vertical.addWidget(favoritesbutton)
        left_layout_vertical.addWidget(spotifybutton)
        left_layout_vertical.addWidget(settingsbutton)

        if(RaspiFM().spotify_isplaying()):
            self.__mainwidget.layout().addWidget(SpotifyWidget(), stretch=4)
        else:
            RaspiFM()
            radiowidget = RadioWidget(True)
            radiowidget.playstarting.connect(self.__stopspotify)
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
        
        if(utils.str_isnullorwhitespace(self.__spotify_dbusname)):
            #if spotify is not up, listen for it to come up
            self.__system_dbusconnection.connect(dbusstrings.dbusservice, dbusstrings.dbuspath, dbusstrings.dbusinterface, dbusstrings.dbussignalnameownerchanged, self.__dbus_nameownerchanged)
        else:
            #if spotify is up, listen to player/track changes
            self.__system_dbusconnection.connect(self.__spotify_dbusname, dbusstrings.spotifydpath, dbusstrings.dbuspropertiesinterface, dbusstrings.dbussignalpropertieschanged, self.__spotifyd_propertieschanged)

            interface = QtDBus.QDBusInterface(self.__spotify_dbusname, dbusstrings.spotifydpath, dbusstrings.dbuspropertiesinterface, self.__system_dbusconnection)
            message = interface.call(dbusstrings.dbusmethodget, dbusstrings.spotifydinterface, dbusstrings.spotifydpropertyplaybackstatus)
            state = message.arguments()[0]
            if(state == "Playing"):
                message = interface.call(dbusstrings.dbusmethodget, dbusstrings.spotifydinterface, dbusstrings.spotifydpropertymetadata)
                metadata = message.arguments()[0]
                RaspiFM().spotify_set_currentplaying(SpotifyInfo(metadata[dbusstrings.spotifydmetadatatitle], metadata[dbusstrings.spotifydmetadataalbum], metadata[dbusstrings.spotifydmetadataartists], metadata[dbusstrings.spotifydmetadataarturl]))

    @pyqtSlot(QtDBus.QDBusMessage)
    def __dbus_nameownerchanged(self, msg:QtDBus.QDBusMessage) -> None:
        args = msg.arguments()
        servicename = args[0]
        newowner = args[1]
        oldowner = args[2]

        if(servicename.startswith("org.mpris.MediaPlayer2.spotifyd.instance")):
            #service new on the bus
            if(utils.str_isnullorwhitespace(newowner)):
                self.__system_dbusconnection.disconnect(dbusstrings.dbusservice, dbusstrings.dbuspath, dbusstrings.dbusinterface, dbusstrings.dbussignalnameownerchanged, self.__dbus_nameownerchanged)
                self.__spotify_dbusname = servicename
                self.__system_dbusconnection.connect(self.__spotify_dbusname, dbusstrings.spotifydpath, dbusstrings.dbuspropertiesinterface, dbusstrings.dbussignalpropertieschanged, self.__spotifyd_propertieschanged)

            #service left bus
            if(utils.str_isnullorwhitespace(oldowner)):
                self.__spotify_dbusname = None
                self.__system_dbusconnection.connect(dbusstrings.dbusservice, dbusstrings.dbuspath, dbusstrings.dbusinterface, dbusstrings.dbussignalnameownerchanged, self.__dbus_nameownerchanged)
                self.__spotifystopped()

    @pyqtSlot(QtDBus.QDBusMessage)
    def __spotifyd_propertieschanged(self, msg:QtDBus.QDBusMessage) -> None:
        changeproperties = msg.arguments()[1]

        #Sometimes, not reproducable, not alle infos are in the changeproperties, onyl one attribute like volume is in it.
        #Normaly after that another propertieschange signal comes in with the full infos.
        if(not dbusstrings.spotifydpropertymetadata in changeproperties or not dbusstrings.spotifydpropertyplaybackstatus in changeproperties):
            return
            #interface = QtDBus.QDBusInterface(self.__spotify_dbusname, dbusstrings.spotifydpath, dbusstrings.dbuspropertiesinterface, self.__system_dbusconnection)
            #msg = interface.call(dbusstrings.dbusmethodgetall, dbusstrings.spotifydinterface)
            #changeproperties = msg.arguments()[0]

        metadata = changeproperties[dbusstrings.spotifydpropertymetadata]
        spotify_wasplaying = RaspiFM().spotify_isplaying()
        RaspiFM().spotify_set_currentplaying(SpotifyInfo(metadata[dbusstrings.spotifydmetadatatitle], metadata[dbusstrings.spotifydmetadataalbum], metadata[dbusstrings.spotifydmetadataartists], metadata[dbusstrings.spotifydmetadataarturl]))
        
        if(changeproperties[dbusstrings.spotifydpropertyplaybackstatus] == "Playing"):
            #no radio widget update necessary, if Plabackstatus is changed from not playing, then SpotifyWidget will be shown.
            #Therefore if the user clicks back to radio, it loads in correct current state
            RaspiFM().player_stop()
            
            if(not spotify_wasplaying):
                if(isinstance(self.__mainwidget.layout().itemAt(1).widget(), SpotifyWidget)):
                    self.__mainwidget.layout().itemAt(1).widget().spotifyupdate()
                else:
                    spotifywidget = SpotifyWidget()
                    spotifywidget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
                    widgetitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), spotifywidget)
                    self.__closewidgetitem(widgetitem)
        else:
            if(RaspiFM().spotify_isplaying()):
                RaspiFM().spotify_set_isplaying(False)

                if(isinstance(self.__mainwidget.layout().itemAt(1).widget(), SpotifyWidget)):
                    self.__mainwidget.layout().itemAt(1).widget().spotifyupdate()   
    
    def __stopspotify(self) -> None:
        interface = QtDBus.QDBusInterface(self.__spotify_dbusname, dbusstrings.spotifydpath, dbusstrings.spotifydinterface, self.__system_dbusconnection)
        interface.call(dbusstrings.spotifydmethodpause)

    def __radioclicked(self) -> None:
        if(not isinstance(self.__mainwidget.layout().itemAt(1).widget(), RadioWidget)):
            radiowidget = RadioWidget(False)
            radiowidget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            radiowidget.playstarting.connect(self.__stopspotify)
            widgetitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), radiowidget)
            self.__closewidgetitem(widgetitem)

    def __favoritelicked(self) -> None:
        self.__stopspotify()
        radiowidget = RadioWidget(True)
        radiowidget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        radiowidget.playstarting.connect(self.__stopspotify)
        widgetitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), radiowidget)
        self.__closewidgetitem(widgetitem)

    def __favoritesclicked(self) -> None:
        if(not isinstance(self.__mainwidget.layout().itemAt(1).widget(), FavoritesWidget)):
            favoriteswdidget = FavoritesWidget()
            favoriteswdidget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            favoriteswdidget.favclicked.connect(self.__favoritelicked)
            widgetitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), favoriteswdidget)
            self.__closewidgetitem(widgetitem)

    def __spotifyclicked(self) -> None:
        if(not isinstance(self.__mainwidget.layout().itemAt(1).widget(), SpotifyWidget)):
            spotifywdidget = SpotifyWidget()
            spotifywdidget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            widgetitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), spotifywdidget)
            self.__closewidgetitem(widgetitem)

    def __settingsclicked(self) -> None:
        if(not isinstance(self.__mainwidget.layout().itemAt(1).widget(), SettingsWidget)):
            settingswdiget = SettingsWidget()
            settingswdiget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            widgetitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), settingswdiget)
            self.__closewidgetitem(widgetitem)

    def __closewidgetitem(self, widgetitem:QWidgetItem) -> None:
        widget = widgetitem.widget()

        if(isinstance(widget, RadioWidget)):
            widget.playstarting.disconnect()

        if(isinstance(widget, FavoritesWidget)):
            widget.favclicked.disconnect()

        widget.close()
        widget.setParent(None)

    def keyPressEvent(self, event): 
        if (event.key() == QtCore.Qt.Key.Key_Escape):
            if(self.isFullScreen()):
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
        RaspiFM().player_shutdown()
        
       
