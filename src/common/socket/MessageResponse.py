from threading import Event

class MessageResponse:
    __slots__ = ["__socket_address", "__message", "__response", "__is_query", "__response_ready", "__transfer_exception", "__message_sent", "__response_exception"]
    __socket_address:str
    __message:dict
    __response:dict
    __is_query:bool
    __message_sent:Event
    __response_ready:Event
    __transfer_exception:Exception
    __response_exception:Exception

    @property
    def socket_address(self) -> str:
        return self.__socket_address
    
    @property
    def message(self) -> dict:
        return self.__message
    
    @property
    def is_query(self) -> bool:
        return self.__is_query
    
    @property
    def message_sent(self) -> Event:
        return self.__message_sent
    
    @property
    def response_ready(self) -> Event:
        return self.__response_ready
    
    @property
    def response(self) -> dict:
        return self.__response
    
    @response.setter
    def response(self, value) -> None:
        self.__response = value

    @property
    def response_exception(self) -> Exception:
        return self.__response_exception
    
    @response_exception.setter
    def response_exception(self, value) -> None:
        self.__response_exception = value

    @property
    def transfer_exception(self) -> Exception:
        return self.__transfer_exception
    
    @transfer_exception.setter
    def transfer_exception(self, value) -> None:
        self.__transfer_exception = value

    def __init__(self, socket_address:str, message:dict, is_query:bool=False):
        self.__socket_address = socket_address
        self.__message = message
        self.__response = None
        self.__is_query = is_query
        self.__message_sent = Event()
        self.__response_ready = Event()
        self.__transfer_exception = None
        self.__response_exception = None