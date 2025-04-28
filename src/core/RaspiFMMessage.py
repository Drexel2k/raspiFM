class RaspiFMMessage:
    __slots__ = ["__message"]
    __message:dict
    
    @property
    def message(self) -> dict:
        return self.__message

    def __init__(self, message:dict):
        self.__message = message