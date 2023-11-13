from flask import render_template, request
from . import app
from ..core.raspifmcore import RaspiFM

core = RaspiFM()

@app.route("/")
def home() -> render_template:
    return render_template("home.html")

@app.route("/favorites")
def favorites() -> render_template:
    return render_template("favorites.html")

@app.route("/stationsearch")
def stationsearch() -> render_template:
    args = request.args
    
    if args and args["name"]:
        #prevlink = 
        #nextlink=
        return render_template("stationsearch.html",
                               stations=core.get_stations(args["name"], args["country"], args["orderby"].lower(), False if args["order"] == "ASC" else True), 
                               countries=core.get_countries(),
                               languages=core.get_languages(),
                               args=args)
    else:
        return render_template("stationsearch.html",
                               countries=core.get_countries(),
                               languages=core.get_languages(),)