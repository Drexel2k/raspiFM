import os

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QSpacerItem

from touchui.socket.RaspiFMProxy import RaspiFMProxy

class SettingsWidget(QWidget):
    __slots__ = ["__cbo_startwith"]

    __cbo_startwith:QComboBox

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        layout_title = QHBoxLayout()
        lbl_logo = QLabel()
        lbl_logo.setStyleSheet("QLabel { margin-right:10px;}") 
        pixmap = QPixmap("touchui/images/raspifmlogo.png")
        lbl_logo.setPixmap(pixmap)
        layout_title.addWidget(lbl_logo)
        layout_title.addWidget(QLabel("raspiFM"))
        layout_title.addStretch()
        lbl_version = QLabel(f'v{RaspiFMProxy().raspifm_getversion()}')
        lbl_version.setStyleSheet("QLabel { font-size:15px;}") #Font-size ist set in qt-material css and can only be overriden in css 
        layout_title.addWidget(lbl_version)
        layout.addLayout(layout_title)
        layout.addItem(QSpacerItem(7, 7))

        lbl_startwith = QLabel("Start with:")
        lbl_startwith.setStyleSheet("QLabel { font-size:28px;}")
        layout.addWidget(lbl_startwith)
        
        self.__cbo_startwith = QComboBox()
        self.__cbo_startwith.setFixedHeight(50)
        self.__cbo_startwith.setStyleSheet(f'QComboBox {{ color:white; }} QComboBox:focus {{ color:{os.environ["QTMATERIAL_PRIMARYCOLOR"]}; }}')
        self.__cbo_startwith.addItem("Last Radiostation", 1) #StartWith.LastStation
        self.__cbo_startwith.addItem("Default Favorite List", 2) #StartWith.DefaultList

        if RaspiFMProxy().settings_touch_startwith() == 2: #StartWith.DefaultList
            self.__cbo_startwith.setCurrentIndex(1)

        self.__cbo_startwith.currentIndexChanged.connect(self.__startwith_selectionchanges)
        layout.addWidget(self.__cbo_startwith)
        layout.addStretch()

        layout.addStretch()       

    def __startwith_selectionchanges(self):
        RaspiFMProxy().settings_set_touch_startwith(self.__cbo_startwith.currentData())
