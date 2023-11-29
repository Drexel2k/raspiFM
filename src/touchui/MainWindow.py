from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QSizePolicy

from .RadioWidget import RadioWidget
from .PushButtonMain import PushButtonMain

class MainWindow(QMainWindow):
    __slots__ = []
    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("raspiFM touch")
        
        main_layout_horizontal = QHBoxLayout()
        widget = QWidget()
        widget.setLayout(main_layout_horizontal)
        self.setCentralWidget(widget)

        left_layout_vertical = QVBoxLayout()
        main_layout_horizontal.addLayout(left_layout_vertical, stretch=1)
        main_layout_horizontal.addWidget(RadioWidget(), stretch=4)
        
        radiobutton = PushButtonMain()
        radiobutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        radioIcon = QIcon("src/webui/static/broadcast-pin-blue.svg")
        radiobutton.setIcon(radioIcon)

        favbutton = PushButtonMain()
        favbutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        favIcon = QIcon("src/webui/static/star-blue.svg")
        favbutton.setIcon(favIcon)

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

