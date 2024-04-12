def str_isnullorwhitespace(arg:str) -> bool:
    if arg is None:
        return True
    
    return arg.isspace()
    