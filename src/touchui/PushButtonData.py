from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QPushButton

        
class PushButtonData(QPushButton):
    __slots__ = ["__data", "__clicked"]
    __data:object

    @property
    def clicked(self) -> pyqtSignal:
        return self.__clicked
    
    @property
    def data(self) -> object:
        return self.__data

    def __init__ (self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__data = data
        if not hasattr(self, '__clicked'):
            PushButtonData.__clicked = pyqtSignal(PushButtonData)
   
    def click(self) -> None:
        QPushButton.click(self)
        self.__clicked.emit(self)
