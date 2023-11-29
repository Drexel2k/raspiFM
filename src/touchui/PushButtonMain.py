from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QSize
        
class PushButtonMain(QPushButton):
    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resizeEvent = self.resized
   
    def resized(self, event) -> None:
        dimension = self.size().height()
        if self.size().width()  < dimension:
            dimension = self.size().width()
        dimension = int(dimension * 0.6)
        self.setIconSize(QSize(dimension, dimension))