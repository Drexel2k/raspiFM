import os
import subprocess
from subprocess import Popen

from common import socketstrings

log = False
if log:
    #sudo mkdir /var/log/raspifm
    #sudo chown raspifm:raspifm /var/log/raspifm
    #core
    log_env = os.environ.copy()
    log_env["PYTHONUNBUFFERED"] = "1"
    core_log = open("/var/log/raspifm/core.log", "w")
    core_process = Popen(["/usr/bin/local/raspifm/.venv/bin/python3", "-m", "core_run"], cwd="/usr/bin/local/raspifm", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=log_env)
    ts_core_process = Popen(["ts", "[%Y-%m-%d %H:%M:%.S]"], stdin=core_process.stdout, stdout=core_log, stderr=subprocess.STDOUT, text=True, env=log_env)
    #spotifyd, more logs in syslog/journal
    spotifyd_log = open("/var/log/raspifm/spotifyd.log", "w")
    spotifyd_process = Popen(["/usr/bin/spotifyd"], cwd="/usr/bin/local/raspifm", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=log_env)
    ts_spotifyd_process = Popen(["ts", "[%Y-%m-%d %H:%M:%.S]"], stdin=spotifyd_process.stdout, stdout=spotifyd_log, stderr=subprocess.STDOUT, text=True, env=log_env)
    #gunicorn socket
    gunicorn_log = open("/var/log/raspifm/gunicorn.log", "w")
    gunicorn_process = Popen(["/usr/bin/local/raspifm/.venv/bin/python3", "-m", "gunicorn", "--name", "raspifm web", "--error-log", "/var/log/raspifm/gunicorn_error_internal.log", "--access-logfile", "/var/log/raspifm/gunicorn_access.log", "--log-level", "debug", "--timeout", "120", "--workers", "1", "--bind", socketstrings.web_socketpath_string, "-m", "007", "webui_run:app"], cwd="/usr/bin/local/raspifm", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=log_env)
    ts_gunicorn_process = Popen(["ts", "[%Y-%m-%d %H:%M:%.S]"], stdin=gunicorn_process.stdout, stdout=gunicorn_log, stderr=subprocess.STDOUT, text=True, env=log_env)
    #touchui
    touchui_log = open("/var/log/raspifm/touchui.log", "w")
    touchui_process = Popen(["/usr/bin/local/raspifm/.venv/bin/python3", "-m", "touchui_run"], cwd="/usr/bin/local/raspifm", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=log_env)
    ts_touchui_process = Popen(["ts", "[%Y-%m-%d %H:%M:%.S]"], stdin=touchui_process.stdout, stdout=touchui_log, stderr=subprocess.STDOUT, text=True, env=log_env)
else:
    #core
    Popen(["/usr/bin/local/raspifm/.venv/bin/python3", "-m", "core_run"], cwd="/usr/bin/local/raspifm", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    #spotifyd
    Popen(["/usr/bin/spotifyd"], cwd="/usr/bin/local/raspifm")
    #gunicorn socket
    Popen(["/usr/bin/local/raspifm/.venv/bin/python3", "-m", "gunicorn", "--name", "raspifm web", "--timeout", "120", "--workers", "1", "--bind", socketstrings.web_socketpath_string, "-m", "007", "webui_run:app"], cwd="/usr/bin/local/raspifm", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    #touchui
    Popen(["/usr/bin/local/raspifm/.venv/bin/python3", "-m", "touchui_run"], cwd="/usr/bin/local/raspifm", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)