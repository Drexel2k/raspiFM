utf8_string = "utf-8"

def str_isnullorwhitespace(arg:str) -> bool:
    if arg is None or len(arg) <= 0:
        return True
        
    return arg.isspace()
