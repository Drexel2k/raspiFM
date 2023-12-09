from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QVBoxLayout,QHBoxLayout, QWidget, QMainWindow, QSizePolicy, QScrollArea, QLabel, QPushButton, QWidgetItem, QLayout

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
        
        widget = QWidget()
        self.__mainwidget = widget
        widget.setLayout(QHBoxLayout())

        self.scroll.setWidget(widget)
        self.setCentralWidget(self.scroll)

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
            RaspiFM().spotify_pause()
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

            return True
        else:
            return False
        
    def __refreshlicked(self) -> None:
        self.__init()

    def __radioclicked(self) -> None:
        if(not isinstance(self.__mainwidget.layout().itemAt(1).widget(), RadioWidget)):
            radiowdiget = RadioWidget()
            radiowdiget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            widgetitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), radiowdiget)

            widget = widgetitem.widget()
            if(isinstance(widget, FavoritesWidget)):
                MainWindow.disconnect(widget, None, None, None)

            widget.close()
            widget.setParent(None)

    def __favclicked(self) -> None:
        if(not isinstance(self.__mainwidget.layout().itemAt(1).widget(), FavoritesWidget)):
            favoriteswdiget = FavoritesWidget()
            favoriteswdiget.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            favoriteswdiget.favclicked.connect(self.__radioclicked)
            widgetitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), favoriteswdiget)
            widgetitem.widget().close()
            widgetitem.widget().setParent(None)

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
        
       
