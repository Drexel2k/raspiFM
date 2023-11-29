import base64

from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QSlider
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

import vlc
from vlc import MediaPlayer

from ..core.raspifmcore import RaspiFM

class RadioWidget(QWidget):
    __slots__ = ["__vlcinstance", "__vlcplayer", "__playcontrolbutton"]
    __vlcinstance:vlc.Instance
    __vlcplayer: MediaPlayer
    __playcontrolbutton:QPushButton

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__vlcinstance = vlc.Instance()
        self.__vlcplayer = self.__vlcinstance.media_player_new()

        volume = 50
        media = self.__vlcinstance.media_new(RaspiFM().favorites_getdefaultlist().stations[0].url)
        self.__vlcplayer.set_media(media)
        self.__vlcplayer.audio_set_volume(volume) 

        self.__vlcplayer.play()

        main_layout_vertical = QVBoxLayout()
        self.setLayout(main_layout_vertical)
 
        qx = QPixmap()
        qx.loadFromData(base64.b64decode(RaspiFM().favorites_getdefaultlist().stations[0].faviconb64), "PNG")
        stationimagelabel = QLabel()
        stationimagelabel.setPixmap(qx)
        stationimagelabel.setStyleSheet("QLabel { background-color : red; color : blue; }")
        main_layout_vertical.addWidget(stationimagelabel, alignment = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        playcontrolbutton = QPushButton("Stop")
        playcontrolbutton.clicked.connect(self.playcontrol_clicked)
        playcontrolbutton.setFixedWidth(100)
        self.__playcontrolbutton = playcontrolbutton
        main_layout_vertical.addWidget(playcontrolbutton, alignment = Qt.AlignmentFlag.AlignHCenter)

        main_layout_vertical.addStretch()


        volslider = QSlider(Qt.Orientation.Horizontal)
        volslider.sliderMoved.connect(self.volslider_moved)
        volslider.setValue(volume)
        main_layout_vertical.addWidget(volslider)

    def playcontrol_clicked(self) -> None:
        if(self.__vlcplayer.is_playing()):
            self.__vlcplayer.stop()
            self.__playcontrolbutton.setText("Play")
        else:
            self.__vlcplayer.play()
            self.__playcontrolbutton.setText("Stop")


    def volslider_moved(self, value:int) -> None:
       self.__vlcplayer.audio_set_volume(value)

