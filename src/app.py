import threading
from .webui import app
from .webui import views

print("http://127.0.0.1:5000/stationsearch")
def starttouchui():
    from . import touchui

x = threading.Thread(target=starttouchui)
x.start()