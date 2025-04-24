import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from touchui.socket.RaspiFMProxy import RaspiFMProxy
from touchui.MainWindow import MainWindow

app = QApplication([])
apply_stylesheet(app, theme="touchui/dark_rpi.xml", css_file=f'{os.getcwd()}/touchui/raspiFM.css')

window = MainWindow()
window.resize(800, 480)

if RaspiFMProxy().settings_runontouch():
    app.setOverrideCursor(Qt.CursorShape.BlankCursor)
    window.showFullScreen()

window.show()

app.exec()