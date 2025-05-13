import subprocess
from subprocess import Popen

from common import strings

log = False
if log:
    #sudo mkdir /var/log/raspifm
    #sudo chown raspifm:raspifm /var/log/raspifm
    #core
    core_out_log = open("/var/log/raspifm/core_out.log", "w")
    core_err_log = open("/var/log/raspifm/core_err.log", "w")
    Popen(["/usr/bin/local/raspifm/.venv/bin/python3", "-m", "core_run"], cwd="/usr/bin/local/raspifm", stdout=core_out_log, stderr=core_err_log)
    #spotifyd, more logs in syslog/journal
    spotifyd_out_log = open("/var/log/raspifm/spotifyd_out.log", "w")
    spotifyd_err_log = open("/var/log/raspifm/spotifyd_err.log", "w")
    Popen(["/usr/bin/spotifyd"], cwd="/usr/bin/local/raspifm", stdout=spotifyd_out_log, stderr=spotifyd_err_log)
    #gunicorn socket
    gunicorn_out_log = open("/var/log/raspifm/gunicorn_out.log", "w")
    gunicorn_err_log = open("/var/log/raspifm/gunicorn_err.log", "w")
    Popen(["/usr/bin/local/raspifm/.venv/bin/python3", "-m", "gunicorn", "--name", "raspifm web", "--error-log", "/var/log/raspifm/gunicorn_error_internal.log", "--access-logfile", "/var/log/raspifm/gunicorn_access.log", "--log-level", "debug", "--timeout", "120", "--workers", "1", "--bind", strings.web_socketpath_string, "-m", "007", "webui_run:app"], cwd="/usr/bin/local/raspifm", stdout=gunicorn_out_log, stderr=gunicorn_err_log)
    #touchui
    touchui_out_log = open("/var/log/raspifm/touchui_out.log", "w")
    touchui_err_log = open("/var/log/raspifm/touchui_err.log", "w")
    Popen(["/usr/bin/local/raspifm/.venv/bin/python3", "-m", "touchui_run"], cwd="/usr/bin/local/raspifm", stdout=touchui_out_log, stderr=touchui_err_log)
else:
    #core
    Popen(["/usr/bin/local/raspifm/.venv/bin/python3", "-m", "core_run"], cwd="/usr/bin/local/raspifm", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    #spotifyd
    Popen(["/usr/bin/spotifyd"], cwd="/usr/bin/local/raspifm")
    #gunicorn socket
    Popen(["/usr/bin/local/raspifm/.venv/bin/python3", "-m", "gunicorn", "--name", "raspifm web", "--timeout", "120", "--workers", "1", "--bind", strings.web_socketpath_string, "-m", "007", "webui_run:app"], cwd="/usr/bin/local/raspifm", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    #touchui
    Popen(["/usr/bin/local/raspifm/.venv/bin/python3", "-m", "touchui_run"], cwd="/usr/bin/local/raspifm", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)