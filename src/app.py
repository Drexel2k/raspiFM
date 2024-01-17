import threading
from webui.web import app
from webui.web import views

def starttouchui():
    from touchui import touch

touchthread = threading.Thread(target=starttouchui)
touchthread.start()

if __name__ == "__main__":
    app.run()