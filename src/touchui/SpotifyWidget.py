from types import MethodType

from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

from core.http.basics import httpcontent
from core.players.Spotify import Spotify
from touchui.MarqueeLabel import MarqueeLabel

class SpotifyWidget(QWidget):
    __slots__ = ["__artlabel" , "__lbl_title", "__lbl_artists", "__lbl_album"]
    __artlabel:QLabel
    __lbl_title:MarqueeLabel
    __lbl_artists:MarqueeLabel
    __lbl_album:MarqueeLabel

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.__artlabel = QLabel()
        layout.addWidget(self.__artlabel, alignment = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        self.__lbl_title = MarqueeLabel()
        self.__lbl_title.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.__lbl_title.setMaximumWidth(self.width() - 40) # If not done, UI will do jerk on time, when widget is opened.
        self.__lbl_title.setStyleSheet("QLabel { font-size:36px; }") #Font-size ist set in qt-material css and can only be overriden in css  
        layout.addWidget(self.__lbl_title, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.__lbl_artists = MarqueeLabel()
        self.__lbl_artists.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.__lbl_artists.setMaximumWidth(self.width() - 40) # If not done, UI will do jerk on time, when widget is opened.
        self.__lbl_artists.setStyleSheet("QLabel { font-size:36px; }") #Font-size ist set in qt-material css and can only be overriden in css  
        layout.addWidget(self.__lbl_artists, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.__lbl_album = MarqueeLabel()
        self.__lbl_album.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.__lbl_album.setMaximumWidth(self.width() - 40) # If not done, UI will do jerk on time, when widget is opened.
        self.__lbl_album.setStyleSheet("QLabel { font-size:36px; }") #Font-size ist set in qt-material css and can only be overriden in css  
        layout.addWidget(self.__lbl_album, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addStretch()
        self.__updatecontentwidgets()        

    def spotifyupdate(self) -> None:
        self.__updatecontentwidgets()

    def __updatecontentwidgets(self) -> None:
        qx = QPixmap()
        if(Spotify().isplaying):
            if(Spotify().currentlyplaying):
                if(Spotify().currentlyplaying.arturl):
                    qx.loadFromData(httpcontent.get_urlbinary_content(Spotify().currentlyplaying.arturl))
                else:
                    renderer =  QSvgRenderer("touchui/images/spotify-blue.svg")
                    image = QImage(270, 270, QImage.Format.Format_ARGB32)
                    image.fill(0x00000000)
                    painter = QPainter(image)
                    renderer.render(painter)
                    painter.end()
                    qx.convertFromImage(image)

            self.__lbl_title.setText(Spotify().currentlyplaying.title)
            self.__lbl_artists.setText(Spotify().currentlyplaying.artists)
            self.__lbl_album.setText(Spotify().currentlyplaying.album)
        else:
            renderer =  QSvgRenderer("touchui/images/spotify-blue.svg")
            image = QImage(180, 180, QImage.Format.Format_ARGB32)
            image.fill(0x00000000)
            painter = QPainter(image)
            renderer.render(painter)
            painter.end()
            qx.convertFromImage(image)

            self.__lbl_title.setText(None)
            self.__lbl_artists.setText(None)
            self.__lbl_album.setText(None)

        self.__artlabel.setPixmap(qx.scaledToHeight(270, Qt.TransformationMode.SmoothTransformation))

    def resizeEvent(self, event) -> None:
        QWidget.resizeEvent(self, event)
        self.__lbl_title.setMaximumWidth(self.width() - 20)
        self.__lbl_artists.setMaximumWidth(self.width() - 20)
        self.__lbl_album.setMaximumWidth(self.width() - 20)