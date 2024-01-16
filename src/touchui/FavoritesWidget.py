import os
import base64

from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtGui import QPixmap, QIcon, QImage, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox

from ..core.http.radiobrowserapi import stationapi
from ..core.players.Vlc import Vlc
from .PushButtonData import PushButtonData
from ..core.RaspiFM import RaspiFM

class FavoritesWidget(QWidget):
    __slots__ = ["__cbo_favoritelists", "__layout"]
    __cbo_favoritelists:QComboBox
    __layout:QVBoxLayout

    favclicked = pyqtSignal()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__layout = QVBoxLayout()
        self.setLayout(self.__layout)
        self.__cbo_favoritelists = QComboBox()

        self.__cbo_favoritelists.setFixedHeight(50)
        self.__cbo_favoritelists.setStyleSheet(f'QComboBox {{ color:white; }} QComboBox:focus {{ color:{os.environ["QTMATERIAL_PRIMARYCOLOR"]}; }}')
        for list in RaspiFM().favorites_getlists():
            self.__cbo_favoritelists.addItem(list.name, list)
        self.__cbo_favoritelists.currentIndexChanged.connect(self.__selectionchange)
        self.__layout.addWidget(self.__cbo_favoritelists)
        self.__layout.addStretch()

        self.__updatefavoritesbuttons()

    def __selectionchange(self):
        self.__updatefavoritesbuttons()

    def __updatefavoritesbuttons(self) -> None:
        while self.layout().count() > 2: #stretch and combobox always contained
            layoutitem = self.layout().takeAt(1) # 0 = combobox, max0 spacer, everything between = Buttons
            btn = layoutitem.widget()
            btn.close()
            btn.setParent(None)

        favoritelist = self.__cbo_favoritelists.currentData()
        for station in favoritelist.stations: 
            button = PushButtonData(station)
            button.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            button.setMaximumWidth(self.width() - 40) # If not done, UI will do jerk on time, when widget is opened.
            button.setFixedHeight(50)
            button.setStyleSheet("QPushButton { text-align:left; }")

            if(station.faviconb64):
                qx = QPixmap()
                qx.loadFromData(base64.b64decode(station.faviconb64), f'{station.faviconextension}')
            else:
                renderer =  QSvgRenderer("src/touchui/images/broadcast-pin-blue.svg")
                image = QImage(42, 42, QImage.Format.Format_ARGB32)
                image.fill(0x00000000)
                painter = QPainter(image)
                renderer.render(painter)
                painter.end()
                qx.convertFromImage(image)

            favIcon = QIcon(qx)
            button.setIconSize(QSize(42, 42))
            button.setIcon(favIcon)

            button.setText(f' {station.name}')
            button.clicked.connect(self.__buttonclicked)
            self.__layout.insertWidget(self.__layout.count() - 1, button)

    @pyqtSlot()
    def __buttonclicked(self):
        Vlc().play(self.sender().data)
        
        if(RaspiFM().settings_runontouch()): #otherwise we are on dev most propably so we don't send a click on every play
            stationapi.send_stationclicked(self.sender().data.uuid)

        self.favclicked.emit()

    def resizeEvent(self, event):
        QWidget.resizeEvent(self, event)
        if self.layout().count() > 2:
            itemindex = 1
            while itemindex < self.layout().count() - 1: #spacer at end
                layoutitem = self.layout().itemAt(itemindex)
                layoutitem.widget().setMaximumWidth(self.width() - 20)
                itemindex +=1
