import os
import base64

from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtGui import QPixmap, QIcon, QImage, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QScrollArea

from common import utils
from touchui.PushButtonData import PushButtonData
from touchui.socket.RaspiFMQtProxy import RaspiFMQtProxy

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

        for list in sorted(RaspiFMQtProxy().favorites_getlists(), key=lambda favlistinternal: favlistinternal["displayorder"]):
            name = list["name"] if not utils.str_isnullorwhitespace(list["name"]) else "List w/o name"
            self.__cbo_favoritelists.addItem(name, list)
        self.__cbo_favoritelists.currentIndexChanged.connect(self.__favoritelists_selectionchanged)

        mainlayout.addWidget(self.__cbo_favoritelists)
        mainlayout.addWidget(scrollarea) 

        self.__scrolllayout.addStretch()

        self.__update_favoritesbuttons()

    def __favoritelists_selectionchanged(self):
        self.__update_favoritesbuttons()

    def __update_favoritesbuttons(self) -> None:
        while self.__scrolllayout.count() > 1: #stretch always contained
            layoutitem = self.__scrolllayout.takeAt(0)
            btn = layoutitem.widget()
            btn.close()
            btn.setParent(None)

        favoritelist = self.__cbo_favoritelists.currentData()
        for station in sorted(favoritelist["stations"], key=lambda stationinternal: stationinternal["displayorder"]):
            station = station["radiostation"]
            button = PushButtonData(station)
            button.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            button.setMaximumWidth(self.width() - 45)
            button.setFixedHeight(50)
            button.setStyleSheet("QPushButton { text-align:left; }")

            qx = QPixmap()
            if not station["faviconb64"] is None:
                qx.loadFromData(base64.b64decode(station["faviconb64"]), f'{station["faviconextension"]}')
            else:
                renderer =  QSvgRenderer("touchui/images/broadcast-pin-rpi.svg")
                image = QImage(61, 42, QImage.Format.Format_ARGB32)
                image.fill(0x00000000)
                painter = QPainter(image)
                renderer.render(painter)
                painter.end()
                qx.convertFromImage(image)

            favIcon = QIcon(qx)
            button.setIconSize(QSize(61, 42))
            button.setIcon(favIcon)

            button.setText(f' {station["name"]}')
            button.clicked.connect(self.__buttonclicked)
            self.__scrolllayout.insertWidget(self.__scrolllayout.count() - 1, button)

    @pyqtSlot()
    def __buttonclicked(self):
        RaspiFMQtProxy().radio_play(self.sender().data["uuid"])

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