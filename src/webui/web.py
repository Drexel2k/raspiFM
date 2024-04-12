from uuid import UUID

from flask import Flask  # Import the Flask class
app = Flask(__name__)    # Create an instance of the class for our use
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.jinja_env.filters["strtouuid"] = UUID

from webui import views

# Time-saver: output a URL to the VS Code terminal so you can easily Ctrl+click to open a browser
print("http://127.0.0.1:5000/favorites")