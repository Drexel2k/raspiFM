import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from ..core.RaspiFM import RaspiFM

from .MainWindow import MainWindow

app = QApplication([])
apply_stylesheet(app, theme="dark_blue.xml", css_file=f'{os.getcwd()}/src/touchui/raspiFM.css')

window = MainWindow()
window.resize(800, 480)

if(RaspiFM().settings.touch_runontouch):
    app.setOverrideCursor(Qt.CursorShape.BlankCursor)
    window.showFullScreen()

window.show()

app.exec()