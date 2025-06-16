from uuid import UUID

from flask import Flask

from common import log

log.init_logger(log.web_logger_name)

app = Flask(__name__)    # Create an instance of the class for our use
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.jinja_env.filters["strtouuid"] = UUID


from webui import views