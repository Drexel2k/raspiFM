from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtWidgets import QFrame

from .QPushButtonMain import QPushButtonMain

class MainWindow(QMainWindow):
    __slots__ = ["__buttons"]
    __buttons:list

    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__buttons = []

        self.setWindowTitle("raspiFM touch")
        
        h_main_layout = QHBoxLayout()
        widget = QWidget()
        widget.setLayout(h_main_layout)
        self.setCentralWidget(widget)

        left_layout = QVBoxLayout()
        h_main_layout.addLayout(left_layout, stretch=1)
        h_main_layout.addWidget(QFrame(), stretch=4)
        
        radiobutton = QPushButtonMain()
        radiobutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        radioIcon = QIcon("src/webui/static/broadcast-pin-blue.svg")
        radiobutton.setIcon(radioIcon)
        self.__buttons.append(radiobutton)

        favbutton = QPushButtonMain()
        favbutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        favIcon = QIcon("src/webui/static/star-blue.svg")
        favbutton.setIcon(favIcon)
        self.__buttons.append(favbutton)

        sptfybutton = QPushButtonMain()
        sptfybutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sptfyIcon = QIcon("src/webui/static/spotify-blue.svg")
        sptfybutton.setIcon(sptfyIcon)
        self.__buttons.append(sptfybutton)

        setbutton = QPushButtonMain()
        setbutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        setIcon = QIcon("src/webui/static/gear-blue.svg")
        setbutton.setIcon(setIcon)
        self.__buttons.append(setbutton)

        left_layout.addWidget(radiobutton)
        left_layout.addWidget(favbutton)
        left_layout.addWidget(sptfybutton)
        left_layout.addWidget(setbutton)  