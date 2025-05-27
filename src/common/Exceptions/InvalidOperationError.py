class InvalidOperationError(Exception):
    slots = ["__code", "__message", "__additional_info_code", "__additional_info_message"]
    __code:int
    __message:str
    __additional_info_code:int
    __additional_info_message:str

    @property
    def code(self) -> int:
        return self.__code
    
    @property
    def message(self) -> str:
        return self.__message
    
    @property
    def additional_info_code(self) -> int:
        return self.__additional_info_code
    
    @property
    def additional_info_message(self) -> str:
        return self.__additional_info_message

    def __init__(self, code:int, message:str, additional_info_code:int, additional_info_message:str):
        super().__init__(message)
        self.__code = code
        self.__message = message
        self.__additional_info_code = additional_info_code
        self.__additional_info_message = additional_info_message