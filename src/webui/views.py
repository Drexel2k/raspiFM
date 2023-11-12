from flask import render_template, request
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
    args = request.args
    if args:
        if not args["name"]:
            return render_template("stationsearch.html")
   
        return render_template("stationsearch.html", stations=core.get_stations(args["name"],args["country"], args["order"], True), args=args)
    else:
        return render_template("stationsearch.html")

    
    #return render_template("stationsearch.html")