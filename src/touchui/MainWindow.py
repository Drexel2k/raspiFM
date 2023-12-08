from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QVBoxLayout,QHBoxLayout, QWidget, QMainWindow, QSizePolicy, QScrollArea

from ..core.radiobrowserapi import stationapi
from ..core.RaspiFM import RaspiFM
from ..core.Vlc import Vlc
from .FavoritesWidget import FavoritesWidget
from .RadioWidget import RadioWidget
from .PushButtonMain import PushButtonMain

class MainWindow(QMainWindow):
    __slots__ = ["__mainwidget"]
    __mainwidget:QWidget

    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("raspiFM touch")
        self.scroll = QScrollArea()
        
        main_layout_horizontal = QHBoxLayout()
        widget = QWidget()
        self.__mainwidget = widget
        widget.setFixedSize(500,500)
        widget.setLayout(main_layout_horizontal)

        self.scroll.setWidget(widget)
        self.setCentralWidget(self.scroll)

        left_layout_vertical = QVBoxLayout()
        main_layout_horizontal.addLayout(left_layout_vertical, stretch=1)

        startstation = RaspiFM().favorites_getdefaultlist().stations[0]
        RaspiFM().spotify_pause()
        Vlc(startstation)
        if(RaspiFM().settings.touch_runontouch): #otherwise we are on dev most propably so we don't send a click on every play
            stationapi.send_stationclicked(startstation.uuid)

        radiowdiget = RadioWidget()
        radiowdiget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        main_layout_horizontal.addWidget(radiowdiget, stretch=4)
        
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

    def __radioclicked(self) -> None:
        if(not isinstance(self.__mainwidget.layout().itemAt(1).widget(), RadioWidget)):
            radiowdiget = RadioWidget()
            radiowdiget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            layoutitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), radiowdiget)

            widget = layoutitem.widget()
            if(isinstance(widget, FavoritesWidget)):
                MainWindow.disconnect(widget, None, None, None)

            widget.close()
            widget.setParent(None)

    def __favclicked(self) -> None:
        if(not isinstance(self.__mainwidget.layout().itemAt(1).widget(), FavoritesWidget)):
            favoriteswdiget = FavoritesWidget()
            favoriteswdiget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            favoriteswdiget.favclicked.connect(self.__radioclicked)
            layoutitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), favoriteswdiget)
            layoutitem.widget().close()
            layoutitem.widget().setParent(None)

    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_Escape):
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
        
       
