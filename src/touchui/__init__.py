from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from .MainWindow import MainWindow

from ..core import raspifmsettings  

app = QApplication([])
apply_stylesheet(app, theme="dark_blue.xml")

window = MainWindow()
if(raspifmsettings.touch_startfullscreen):
    window.showFullScreen()
else:
    window.resize(800, 480)

window.show()

app.exec()

