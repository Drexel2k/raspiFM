from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from ..core import raspifmsettings

class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

class MainWindow(QMainWindow):
    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("raspiFM touch")
        
        h_main_layout = QHBoxLayout()
        widget = QWidget()
        widget.setLayout(h_main_layout)
        self.setCentralWidget(widget)

        left_layout = QVBoxLayout()
        h_main_layout.addLayout(left_layout, stretch=1)
        h_main_layout.addWidget(QFrame(), stretch=4)
        
        radiobutton = QPushButton("R")
        radiobutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        favbutton = QPushButton("F")
        favbutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        sptfybutton = QPushButton("Sp")
        sptfybutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        setbutton = QPushButton("Se")
        setbutton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        left_layout.addWidget(radiobutton)
        left_layout.addWidget(favbutton)
        left_layout.addWidget(sptfybutton)
        left_layout.addWidget(setbutton)

app = QApplication([])

window = MainWindow()
if(raspifmsettings.touch_startfullscreen):
    window.showFullScreen()
else:
    window.resize(800, 480)

window.show()

app.exec()

