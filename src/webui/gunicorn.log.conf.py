from common import socketstrings
import webui_run
proc_name = "raspifm web"
timeout = 120
workers = 1
bind = socketstrings.web_socketpath_string
umask = 7
errorlog = "/var/log/raspifm/gunicorn_internal.log"
accesslog = "/var/log/raspifm/gunicorn_access.log"
loglevel = "debug"

worker_exit = webui_run.worker_exit