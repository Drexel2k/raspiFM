from PyQt6 import QtDBus, QtCore
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QVBoxLayout,QHBoxLayout, QWidget, QMainWindow, QSizePolicy, QScrollArea, QLabel, QPushButton, QWidgetItem, QLayout

from ..utils import utils
from ..core.radiobrowserapi import stationapi
from ..core.RaspiFM import RaspiFM
from ..core.Vlc import Vlc
from .FavoritesWidget import FavoritesWidget
from .RadioWidget import RadioWidget
from .PushButtonMain import PushButtonMain

class MainWindow(QMainWindow):
    __slots__ = ["__mainwidget", "__spotify_dbusname", "__system_dbusconnection"]
    __mainwidget:QWidget
    __spotify_dbusname:str
    __system_dbusconnection:QtDBus.QDBusConnection

    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("raspiFM touch")
        self.scroll = QScrollArea()
        
        widget = QWidget()
        self.__mainwidget = widget
        widget.setLayout(QHBoxLayout())

        self.scroll.setWidget(widget)
        self.setCentralWidget(self.scroll)

        self.__spotify_dbusname = None
        self.__system_dbusconnection = None

        if(not self.__init()):
            vertical = QVBoxLayout()
            self.__mainwidget.layout().addLayout(vertical)
            vertical.addStretch()
            label = QLabel("No radio station favorites found,")
            vertical.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
            label = QLabel("go to webinterface (probably http://raspifm),")
            vertical.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
            label = QLabel("save favorites and press refresh.")
            vertical.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
            refreshbutton = QPushButton("Refresh")
            refreshbutton.clicked.connect(self.__refreshlicked)
            vertical.addWidget(refreshbutton)
            vertical.addStretch()

    def __init(self) -> bool:
        defaultlist = RaspiFM().favorites_getdefaultlist()

        if(len(defaultlist.stations) > 0):
            #remove no favorites warning if warning was set before. favorite warning constists of 1 child, the QVBoxLayout, in the main QHBoxLayout,
            #where the normal setup consists of 2 children in the main QHBoxLayout, one QVBoxLayout layout and one widget

            #todo: maybe remove mainwidget oder add a root widget over all the info widget so that only the main or root widget has to be deleted
            # to delte also all sub widgets
            if(self.__mainwidget.layout().count() == 1): 
                layoutitem = self.__mainwidget.layout().takeAt(0)
                for index in reversed(range(layoutitem.count())):
                    item = layoutitem.takeAt(index)
                    #QSpaceritem/QLayoutItem have no parents
                    if(isinstance(item, QWidgetItem) or isinstance(item, QLayout)):
                        item.widget().close()
                        item.widget().setParent(None)

                #QLayout has parent
                layoutitem.setParent(None)

            left_layout_vertical = QVBoxLayout()
            self.__mainwidget.layout().addLayout(left_layout_vertical, stretch=1)

            startstation = RaspiFM().favorites_getdefaultlist().stations[0]
            #RaspiFM().spotify_pause()
            Vlc(startstation)
            if(RaspiFM().settings.touch_runontouch): #otherwise we are on dev most propably so we don't send a click on every play
                stationapi.send_stationclicked(startstation.uuid)

            radiowdiget = RadioWidget()
            radiowdiget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            self.__mainwidget.layout().addWidget(radiowdiget, stretch=4)
            
            radiobutton = PushButtonMain()
            radiobutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding) 
            radiobutton.setIcon(QIcon("src/webui/static/broadcast-pin-blue.svg"))
            radiobutton.clicked.connect(self.__radioclicked)

            favbutton = PushButtonMain()
            favbutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            favbutton.setIcon(QIcon("src/webui/static/star-blue.svg"))
            favbutton.clicked.connect(self.__favclicked)

            sptfybutton = PushButtonMain()
            sptfybutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            sptfybutton.setIcon(QIcon("src/webui/static/spotify-blue.svg"))

            setbutton = PushButtonMain()
            setbutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            setbutton.setIcon(QIcon("src/webui/static/gear-blue.svg"))

            left_layout_vertical.addWidget(radiobutton)
            left_layout_vertical.addWidget(favbutton)
            left_layout_vertical.addWidget(sptfybutton)
            left_layout_vertical.addWidget(setbutton)

            self.__initializespotify()
            return True
        else:
            return False
        
    def __initializespotify(self) -> None:
        self.__system_dbusconnection = QtDBus.QDBusConnection.systemBus()
        self.__system_dbusconnection.registerObject('/', self) #needed to prevent hang of connect call, is a bug, which will be fixed.
        servicenames = self.__system_dbusconnection.interface().registeredServiceNames().value()
        for name in servicenames:
            if name.startswith("org.mpris.MediaPlayer2.spotifyd.instance"):
               self.__spotify_dbusname = name
               break
        
        if(utils.str_isnullorwhitespace(self.__spotify_dbusname)):
            self.__system_dbusconnection.connect("org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus", "NameOwnerChanged", self.__dbus_nameownerchanged)
        else:
            self.__system_dbusconnection.connect(self.__spotify_dbusname, "/org/mpris/MediaPlayer2", "org.freedesktop.DBus.Properties", "PropertiesChanged", self.__spotifyd_propertieschanged)

    @pyqtSlot(QtDBus.QDBusMessage)
    def __dbus_nameownerchanged(self, msg:QtDBus.QDBusMessage) -> None:
        args = msg.arguments()
        servicename = args[0]
        newowner = args[1]
        oldowner = args[2]

        if(servicename.startswith("org.mpris.MediaPlayer2.spotifyd.instance")):
            #service new on the bus
            if(utils.str_isnullorwhitespace(newowner)):
                self.__system_dbusconnection.disconnect("org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus", "NameOwnerChanged", self.__dbus_nameownerchanged)
                self.__spotify_dbusname = servicename
                self.__system_dbusconnection.connect(self.__spotify_dbusname, "/org/mpris/MediaPlayer2", "org.freedesktop.DBus.Properties", "PropertiesChanged", self.__spotifyd_propertieschanged)

            #service left bus
            if(utils.str_isnullorwhitespace(oldowner)):
                self.__spotify_dbusname = None
                self.__system_dbusconnection.connect("org.freedesktop.DBus", "/org/freedesktop/DBus", "org.freedesktop.DBus", "NameOwnerChanged", self.__dbus_nameownerchanged)

    @pyqtSlot(QtDBus.QDBusMessage)
    def __spotifyd_propertieschanged(self, msg:QtDBus.QDBusMessage) -> None:
        changeproperties = msg.arguments()[1]
        playbackstatus = changeproperties["PlaybackStatus"]
        metadata = changeproperties["Metadata"]
        title = metadata["xesam:title"]
        album = metadata["xesam:album"]
        artists = metadata["xesam:artist"] #list
        arturl = metadata["mpris:artUrl"]
        
    def __refreshlicked(self) -> None:
        self.__init()

    def __radioclicked(self) -> None:
        if(not isinstance(self.__mainwidget.layout().itemAt(1).widget(), RadioWidget)):
            radiowdiget = RadioWidget()
            radiowdiget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            widgetitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), radiowdiget)

            widget = widgetitem.widget()
            if(isinstance(widget, FavoritesWidget)):
                widget.favclicked.disconnect()

            widget.close()
            widget.setParent(None)

    def __favclicked(self) -> None:
        if(not isinstance(self.__mainwidget.layout().itemAt(1).widget(), FavoritesWidget)):
            favoriteswdidget = FavoritesWidget()
            favoriteswdidget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            favoriteswdidget.favclicked.connect(self.__radioclicked)
            widgetitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), favoriteswdidget)
            widgetitem.widget().close()
            widgetitem.widget().setParent(None)

    def spotify_pause(self) -> None:
        service = self.__get_spotifyd_dbus_instance()
        if(service):
            path = "/org/mpris/MediaPlayer2"
            iface = "org.mpris.MediaPlayer2.Player"
            #ifaceprops = "org.freedesktop.DBus.Properties"

            #proxy = dbus.SystemBus().get_object(service, path)
            #proxy.Pause(dbus_interface=iface)
            #vol = interface.Get(iface,"Volume")
            #print(vol)

    def keyPressEvent(self, event): 
        if (event.key() == QtCore.Qt.Key.Key_Escape):
            if(self.isFullScreen()):
                self.showNormal() 
    
    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)
        self.__mainwidget.setFixedSize(self.width(), self.height())

    def closeEvent(self, event) -> None:
        QMainWindow.closeEvent(self, event)
        widget = self.__mainwidget.layout().itemAt(1).widget()
        widget.close()
        widget.setParent(None)
        Vlc().shutdown()
        
       
