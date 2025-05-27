class InvalidOperationError(Exception):
    slots = ["__code", "__message"]
    __code:int
    __message:str

    @property
    def code(self) -> int:
        return self.__code
    
    @property
    def message(self) -> str:
        return self.__message

    def __init__(self, code:int, message:str):
        super().__init__(message)
        self.__code = code
        self.__message = message