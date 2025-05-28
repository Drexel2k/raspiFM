from common import socketstrings
import webui_run
proc_name = "raspifm web"
timeout = 120
workers = 1
bind = socketstrings.web_socketpath_string
umask = 7

worker_exit = webui_run.worker_exit