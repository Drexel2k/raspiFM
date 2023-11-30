from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QSizePolicy

from .FavoritesWidget import FavoritesWidget
from .RadioWidget import RadioWidget
from .PushButtonMain import PushButtonMain

from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtCore import Qt

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
        radio = RadioWidget()
        radio.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        main_layout_horizontal.addWidget(radio, stretch=4)
        
        radiobutton = PushButtonMain()
        radiobutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        radioIcon = QIcon("src/webui/static/broadcast-pin-blue.svg")
        radiobutton.setIcon(radioIcon)
        radiobutton.clicked.connect(self.radioclicked)

        favbutton = PushButtonMain()
        favbutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        favIcon = QIcon("src/webui/static/star-blue.svg")
        favbutton.setIcon(favIcon)
        favbutton.clicked.connect(self.favclicked)

        sptfybutton = PushButtonMain()
        sptfybutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sptfyIcon = QIcon("src/webui/static/spotify-blue.svg")
        sptfybutton.setIcon(sptfyIcon)

        setbutton = PushButtonMain()
        setbutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        setIcon = QIcon("src/webui/static/gear-blue.svg")
        setbutton.setIcon(setIcon)

        left_layout_vertical.addWidget(radiobutton)
        left_layout_vertical.addWidget(favbutton)
        left_layout_vertical.addWidget(sptfybutton)
        left_layout_vertical.addWidget(setbutton)

    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)
        self.__mainwidget.setFixedSize(self.width(), self.height())

    def radioclicked(self) -> None:
        if(not isinstance(self.__mainwidget.layout().itemAt(1).widget(), RadioWidget)):
             layoutitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), RadioWidget())
             layoutitem.widget().close()

    def favclicked(self) -> None:
        if(not isinstance(self.__mainwidget.layout().itemAt(1).widget(), FavoritesWidget)):
           layoutitem = self.__mainwidget.layout().replaceWidget(self.__mainwidget.layout().itemAt(1).widget(), FavoritesWidget())
           layoutitem.widget().setParent(None)
           layoutitem.widget().close()
           layoutitem.widget().deleteLater()
