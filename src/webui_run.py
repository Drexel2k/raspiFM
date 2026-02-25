import logging

#uwsgi needs app object on this level
from webui.run import app
from common.socket.raspifm_client.RaspiFMProxy import RaspiFMProxy

logger = logging.getLogger(__name__)

#on development we use the flask development server, not executed with uwsgi
if __name__ == '__main__':
    # Time-saver: output a URL to the VS Code terminal so you can easily Ctrl+click to open a browser
    print("http://127.0.0.1:5000/stationsearch")
    print("http://127.0.0.1:5000/favorites")
    app.run()
