import logging
import sys

core_logger_name = "raspifm_core"
touch_logger_name = "raspifm_touch"
web_logger_name = "raspifm_web"

def init_logger(name:str):
    logger = logging.getLogger(name)
    logger.propagate = False
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("{levelname}:{name}:{message}", style="{"))
    logger.addHandler(handler)