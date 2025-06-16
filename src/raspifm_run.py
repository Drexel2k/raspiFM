import datetime
import os
import subprocess
from subprocess import Popen

log = False
if log:
    #sudo mkdir /var/log/raspifm
    #sudo chown raspifm:raspifm /var/log/raspifm
    now = datetime.datetime.now()
    started_string = f"[{now.strftime("%Y-%m-%d %H:%M:%S.%f")}] RaspiFM started.\n"
    #core
    log_env = os.environ.copy()
    log_env["PYTHONUNBUFFERED"] = "1"
    core_log = open("/var/log/raspifm/core.log", "a")
    core_log.write(started_string)
    core_process = Popen(["/usr/bin/local/raspifm/.venv/bin/python3", "-m", "core_run"], cwd="/usr/bin/local/raspifm", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=log_env)
    ts_core_process = Popen(["ts", "[%Y-%m-%d %H:%M:%.S]"], stdin=core_process.stdout, stdout=core_log, stderr=subprocess.STDOUT, text=True, env=log_env)
    #spotifyd, more logs in syslog/journal
    spotifyd_log = open("/var/log/raspifm/spotifyd.log", "a")
    spotifyd_log.write(started_string)
    spotifyd_process = Popen(["/usr/bin/spotifyd"], cwd="/usr/bin/local/raspifm", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=log_env)
    ts_spotifyd_process = Popen(["ts", "[%Y-%m-%d %H:%M:%.S]"], stdin=spotifyd_process.stdout, stdout=spotifyd_log, stderr=subprocess.STDOUT, text=True, env=log_env)
    #gunicorn socket
    gunicorn_log = open("/var/log/raspifm/gunicorn.log", "a")
    gunicorn_log.write(started_string)
    gunicorn_process = Popen(["/usr/bin/local/raspifm/.venv/bin/python3", "-m", "gunicorn", "--config", "webui/gunicorn.log.conf.py", "webui_run:app"], cwd="/usr/bin/local/raspifm", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=log_env)
    ts_gunicorn_process = Popen(["ts", "[%Y-%m-%d %H:%M:%.S]"], stdin=gunicorn_process.stdout, stdout=gunicorn_log, stderr=subprocess.STDOUT, text=True, env=log_env)
    #touchui
    touchui_log = open("/var/log/raspifm/touchui.log", "a")
    touchui_log.write(started_string)
    touchui_process = Popen(["/usr/bin/local/raspifm/.venv/bin/python3", "-m", "touchui_run"], cwd="/usr/bin/local/raspifm", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=log_env)
    ts_touchui_process = Popen(["ts", "[%Y-%m-%d %H:%M:%.S]"], stdin=touchui_process.stdout, stdout=touchui_log, stderr=subprocess.STDOUT, text=True, env=log_env)
else:
    #core
    Popen(["/usr/bin/local/raspifm/.venv/bin/python3", "-m", "core_run"], cwd="/usr/bin/local/raspifm", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    #spotifyd
    Popen(["/usr/bin/spotifyd"], cwd="/usr/bin/local/raspifm")
    #gunicorn socket
    Popen(["/usr/bin/local/raspifm/.venv/bin/python3", "-m", "gunicorn", "--config", "webui/gunicorn.conf.py", "webui_run:app"], cwd="/usr/bin/local/raspifm", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    #touchui
    Popen(["/usr/bin/local/raspifm/.venv/bin/python3", "-m", "touchui_run"], cwd="/usr/bin/local/raspifm", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)