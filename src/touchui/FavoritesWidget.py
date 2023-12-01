import os
import base64

from PyQt6.QtCore import Qt
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QPixmap
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QComboBox
from PyQt6.QtWidgets import QPushButton

from .PushButtonData import PushButtonData

from ..core.RaspiFM import RaspiFM

class FavoritesWidget(QWidget):
    __slots__ = ["__cbo_favoritelists", "__layout"]
    __cbo_favoritelists:QComboBox
    __layout:QVBoxLayout
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__layout = QVBoxLayout()
        self.setLayout(self.__layout)
        self.__cbo_favoritelists = QComboBox()
        self.__cbo_favoritelists.setFixedHeight(50)
        self.__cbo_favoritelists.setStyleSheet(f'QComboBox {{ color:white; font-size:30px }} QComboBox:focus {{ color:{os.environ["QTMATERIAL_PRIMARYCOLOR"]}; }}')
        for list in RaspiFM().favorites_getlists():
            self.__cbo_favoritelists.addItem(list.name, list)
        self.__cbo_favoritelists.currentIndexChanged.connect(self.selectionchange)
        self.__layout.addWidget(self.__cbo_favoritelists)
        self.__layout.addStretch()

        self.updatefavoritesbuttons()

    def selectionchange(self, index):
        self.updatefavoritesbuttons()

    def updatefavoritesbuttons(self) -> None:
        while self.layout().count() > 2: #stretch and combobox always contained
            layoutitem = self.layout().takeAt(1)
            btn = layoutitem.widget()
            btn.close()
            btn.setParent(None)


        favoritelist = self.__cbo_favoritelists.currentData()
        for station in favoritelist.stations: 
            button = PushButtonData(station)
            button.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            button.setFixedHeight(50)
            button.setMaximumWidth(self.width() - 40)
            button.setStyleSheet("QPushButton { font-size:30px; text-align:left; }")

            qx = QPixmap()
            qx.loadFromData(base64.b64decode(station.faviconb64), f'{station.faviconextension}')
            favIcon = QIcon(qx)
            button.setIconSize(QSize(42, 42))
            button.setIcon(favIcon)

            button.setText(f' {station.name}')
            self.__layout.insertWidget(1, button)