import threading
from .webui.web import app
from .webui.web import views

print("http://127.0.0.1:5000/stationsearch")
def starttouchui():
    from .touchui import touch

x = threading.Thread(target=starttouchui)
x.start()