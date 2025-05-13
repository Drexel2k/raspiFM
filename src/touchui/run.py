import os

import setproctitle

from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from touchui.MainWindow import MainWindow

setproctitle.setproctitle("raspiFM touch")

app = QApplication([])
apply_stylesheet(app, theme="touchui/dark_rpi.xml", css_file=f'{os.getcwd()}/touchui/raspiFM.css')

window = MainWindow()
window.resize(800, 480)

window.show()
app.exec()