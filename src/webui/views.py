from flask import render_template
from . import app
from src.core.radiobrowserapi import stationapi
import json

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/favorites")
def favorites():
    return render_template("favorites.html")

@app.route("/stationsearch")
def stationsearch():
    data = stationapi.query_stations_advanced()
    return render_template("stationsearch.html", stations=json.loads(data))

