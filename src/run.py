import threading
from .webui import app
from .webui import views

def starttouchui():
    from . import touchui

x = threading.Thread(target=starttouchui)
x.start()