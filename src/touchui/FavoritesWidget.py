import os
import base64

from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtGui import QPixmap, QIcon, QImage, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QScrollArea

from core.http.radiobrowserapi import stationapi
from core.players.Vlc import Vlc
from touchui.PushButtonData import PushButtonData
from core.RaspiFM import RaspiFM

class FavoritesWidget(QWidget):
    __slots__ = ["__cbo_favoritelists", "__scrolllayout"]

    __cbo_favoritelists:QComboBox
    __scrolllayout:QVBoxLayout

    favclicked = pyqtSignal()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        mainlayout = QVBoxLayout()
        self.setLayout(mainlayout)

        scrollwidget = QWidget()
        self.__scrolllayout = QVBoxLayout()
        scrollwidget.setLayout(self.__scrolllayout)
        scrollarea = QScrollArea()
        scrollarea.setWidgetResizable(True)
        scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scrollarea.setWidget(scrollwidget)

        self.__cbo_favoritelists = QComboBox()
        self.__cbo_favoritelists.setFixedHeight(50)
        self.__cbo_favoritelists.setStyleSheet(f'QComboBox {{ color:white; }} QComboBox:focus {{ color:{os.environ["QTMATERIAL_PRIMARYCOLOR"]}; }}')
        for list in RaspiFM().favorites_getlists():
            self.__cbo_favoritelists.addItem(list.name, list)
        self.__cbo_favoritelists.currentIndexChanged.connect(self.__favoritelists_selectionchanged)

        mainlayout.addWidget(self.__cbo_favoritelists)
        mainlayout.addWidget(scrollarea) 

        self.__scrolllayout.addStretch()

        self.__updatefavoritesbuttons()

    def __favoritelists_selectionchanged(self):
        self.__updatefavoritesbuttons()

    def __updatefavoritesbuttons(self) -> None:
        while self.__scrolllayout.count() > 1: #stretch always contained
            layoutitem = self.__scrolllayout.takeAt(0)
            btn = layoutitem.widget()
            btn.close()
            btn.setParent(None)

        favoritelist = self.__cbo_favoritelists.currentData()
        for station in favoritelist.stations: 
            button = PushButtonData(station)
            button.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            button.setMaximumWidth(self.width() - 45)
            button.setFixedHeight(50)
            button.setStyleSheet("QPushButton { text-align:left; }")

            qx = QPixmap()
            if(station.faviconb64):
                qx.loadFromData(base64.b64decode(station.faviconb64), f'{station.faviconextension}')
            else:
                renderer =  QSvgRenderer("touchui/images/broadcast-pin-blue.svg")
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
            self.__scrolllayout.insertWidget(self.__scrolllayout.count() - 1, button)

    @pyqtSlot()
    def __buttonclicked(self):
        RaspiFM().player_play(self.sender().data)

        self.favclicked.emit()

    def resizeEvent(self, event):
        QWidget.resizeEvent(self, event)
        if self.__scrolllayout.count() > 1:
            itemindex = 0
            c = self.__scrolllayout.count()
            while itemindex < self.__scrolllayout.count() - 1: #spacer at end
                layoutitem = self.__scrolllayout.itemAt(itemindex)
                layoutitem.widget().setMaximumWidth(self.width() - 45)
                itemindex +=1


