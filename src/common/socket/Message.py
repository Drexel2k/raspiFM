class RequestResponse:
    __slots__ = ["__socket_address", "__message"]
    __socket_address:str
    __message:dict

    @property
    def socket_address(self):
        return self.__socket_address
    
    @property
    def message(self):
        return self.__message

    def __init__(self, socket_address:str, message:dict):
        self.__socket_address = socket_address
        self.__message = message