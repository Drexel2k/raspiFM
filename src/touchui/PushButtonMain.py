from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QPushButton
        
class PushButtonMain(QPushButton):
    def __init__ (self, *args, **kwargs):
        super().__init__(*args, **kwargs)
   
    def resizeEvent(self, event) -> None:
        dimension = self.size().height()
        if self.size().width()  < dimension:
            dimension = self.size().width()
        dimension = int(dimension * 0.9)
        self.setIconSize(QSize(dimension, dimension))