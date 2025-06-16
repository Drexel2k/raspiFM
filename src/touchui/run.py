import os

import setproctitle

from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from common import log
from touchui.MainWindow import MainWindow

log.init_logger(log.touch_logger_name)

setproctitle.setproctitle("raspiFM touch")

app = QApplication([])
apply_stylesheet(app, theme="touchui/dark_rpi.xml", css_file=f"{os.getcwd()}/touchui/raspiFM.css")

window = MainWindow()
window.show()

app.exec()