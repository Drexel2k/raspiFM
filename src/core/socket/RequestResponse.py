class RequestResponse:
    __slots__ = ["__socket_address", "__request", "__response"]
    __socket_address:str
    __request:dict
    __response:dict

    @property
    def socket_address(self):
        return self.__socket_address
    
    @property
    def request(self):
        return self.__request
    
    @property
    def response(self):
        return self.__response
    
    @response.setter
    def response(self, value):
        self.__response = value

    def __init__(self, socket_address:str, request:dict):
        self.__socket_address = socket_address
        self.__request = request