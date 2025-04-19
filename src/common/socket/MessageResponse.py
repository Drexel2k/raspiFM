from threading import Event

class MessageResponse:
    __slots__ = ["__socket_address", "__message", "__response", "__is_query", "__response_ready"]
    __socket_address:str
    __message:dict
    __response:dict
    __is_query:bool
    __response_ready:Event

    @property
    def socket_address(self):
        return self.__socket_address
    
    @property
    def message(self):
        return self.__message
    
    @property
    def is_query(self):
        return self.__is_query
    
    @property
    def response_ready(self):
        return self.__response_ready
    
    @property
    def response(self):
        return self.__response
    
    @response.setter
    def response(self, value):
        self.__response = value
        if(value is not None):
            self.__response_ready.set()

    def __init__(self, socket_address:str, message:dict, is_query:bool=False):
        self.__socket_address = socket_address
        self.__message = message
        self.__response = None
        self.__is_query = is_query
        self.__response_ready = Event()