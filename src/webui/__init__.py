from flask import Flask  # Import the Flask class
app = Flask(__name__)    # Create an instance of the class for our use
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True