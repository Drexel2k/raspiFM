from PyQt6.QtCore import Qt
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QLabel

class MarqueeLabel(QLabel):
    __slots__ = ["__x", "__y", "__timer", "__speed", "__textLength", "__textHeight"]
    __x:int
    __y:int
    __timer:QTimer
    __speed:float
    __textLength:int
    __textHeight:int

    def __init__(self, parent=None):
        QLabel.__init__(self, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.__timer = QTimer(self)
        self.__timer.timeout.connect(self.update)
        self.__speed = 1.5

    def resizeEvent(self, event):
        self.__timer.stop()
        QLabel.resizeEvent(self, event)
        self.setTextDimensions()
        self.checkScroll()          

    def paintEvent(self, event):
        if(self.__timer.isActive()):
            painter = QPainter(self)
            self.__x -= self.__speed
            if self.__x <= -self.__textLength:
                self.__x = self.width()
            painter.drawText(int(self.__x), int(self.__y + self.__textHeight), self.text())
        else:
            QLabel.paintEvent(self, event)

    def setTextDimensions(self):
        self.__textHeight = self.fontMetrics().height()
        self.__textLength = self.fontMetrics().horizontalAdvance(self.text())
        self.setFixedHeight(self.fontMetrics().height())

    def checkScroll(self) -> None:
        print(self.width())
        if(self.__textLength <= self.width()):
            self.__timer.stop()
        else:
            self.__x = 70
            self.__y = self.height() - self.__textHeight - int(self.__textHeight/4)
            self.__timer.start(40)


