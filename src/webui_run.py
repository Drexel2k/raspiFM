#gunicorn needs app object on this level
from webui.run import app
from common.socket.raspifm_client.RaspiFMProxy import RaspiFMProxy

def worker_exit(server, worker):
    RaspiFMProxy().raspifm_shutdown(False)

#on development we use the flask development server, not executed with gunicorn
if __name__ == '__main__':
    # Time-saver: output a URL to the VS Code terminal so you can easily Ctrl+click to open a browser
    print("http://127.0.0.1:5000/stationsearch")
    print("http://127.0.0.1:5000/favorites")
    app.run()
