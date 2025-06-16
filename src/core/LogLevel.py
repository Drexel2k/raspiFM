from enum import Enum

class LogLevel(Enum):
    Debug = 1
    Info = 2
    Warning = 3
    Error = 4
    Critical = 5
    Nolog = 100