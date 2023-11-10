
from flask import render_template
from . import app

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/favorites")
def favorites():
    return render_template("favorites.html")

@app.route("/stationsearch")
def stationsearch():
    return render_template("stationsearch.html")

