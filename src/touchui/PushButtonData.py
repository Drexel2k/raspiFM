from PyQt6.QtWidgets import QPushButton

class PushButtonData(QPushButton):
    __slots__ = ["__data"]
    __data:object
    
    @property
    def data(self) -> object:
        return self.__data

    def __init__ (self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__data = data