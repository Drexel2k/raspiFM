from flask import render_template
from . import app
from ..core.raspifmcore import RaspiFM

core = RaspiFM()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/favorites")
def favorites():
    return render_template("favorites.html")

@app.route("/stationsearch")
def stationsearch():
    tester = core.get_stations("1live","DE", "clicks", "false")
    return render_template("stationsearch.html", stations=tester)

6