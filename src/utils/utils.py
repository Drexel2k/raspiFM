def str_isnullorwhitespace(arg:str) -> bool:
    if(not arg):
        return True
    
    return arg.isspace()
    