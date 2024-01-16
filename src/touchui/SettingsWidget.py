import os

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel

from ..core.RaspiFM import RaspiFM
from ..core.StartWith import StartWith

class SettingsWidget(QWidget):
    __slots__ = ["__cbo_startwith"]

    __cbo_startwith:QComboBox

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        lbl_startwith = QLabel("Start with:")
        lbl_startwith.setStyleSheet("QLabel { font-size:28px;}") #Font-size ist set in qt-material css and can only be overriden in css 
        layout.addWidget(lbl_startwith)
        
        self.__cbo_startwith = QComboBox()
        self.__cbo_startwith.setFixedHeight(50)
        self.__cbo_startwith.setStyleSheet(f'QComboBox {{ color:white; }} QComboBox:focus {{ color:{os.environ["QTMATERIAL_PRIMARYCOLOR"]}; }}')
        self.__cbo_startwith.addItem("Last Radiostation", StartWith.LastStation)
        self.__cbo_startwith.addItem("Default Favorite List", StartWith.DefaultList)

        if(RaspiFM().settings_touch_startwith() == StartWith.DefaultList):
            self.__cbo_startwith.setCurrentIndex(1)

        self.__cbo_startwith.currentIndexChanged.connect(self.__startwith_selectionchanges)
        layout.addWidget(self.__cbo_startwith)
        layout.addStretch()

        layout.addStretch()       

    def __startwith_selectionchanges(self):
        RaspiFM().settings_changeproperty("startwith", self.__cbo_startwith.currentData().name)
