from flask import make_response, render_template, request

from . import app
from uuid import UUID
from ..core.raspifmcore import RaspiFM
from ..core import raspifmsettings
from ..utils import utils
from .ViewProxies.RadioStationView import RadioStationView

core = RaspiFM()

@app.route("/")
def home() -> render_template:
    return render_template("home.html")

@app.route("/favorites")
def favorites() -> render_template:
    selected = {"favoritelist":core.favorites.getdefault() }

    return render_template("favorites.html",
                           favorites=core.favorites,
                           selected=selected)

@app.route("/stationsearch")
def stationsearch() -> render_template:   
    args = request.args

    stations = []
    countries = core.get_countries()
    languages = core.get_languages()

    selected = {"name":None, "country":raspifmsettings.defaulcountry, "language":raspifmsettings.defaultlanguage, "tags":[], "orderby":"name", "order":"asc", "favoritelist":core.favorites.getdefault() }

    pagelast=1
    pagenext=2

    if args:
        if("name" in args and not utils.str_isnullorwhitespace(args["name"])):
            selected["name"]=args["name"]

        if("country" in args and not utils.str_isnullorwhitespace(args["country"]) and not args["country"]=="nofilter"):
            selected["country"]=args["country"]
        
        if("lang" in args and not utils.str_isnullorwhitespace(args["lang"]) and not args["lang"]=="nofilter"):
            selected["language"]=args["lang"]

        if("tags" in args and not utils.str_isnullorwhitespace(args["tags"])):
            selected["tags"] = args["tags"].split(",")

        if("favoritelist" in args and not utils.str_isnullorwhitespace(args["favoritelist"])):
            selected["favoritelist"] = core.favorites.getlist(UUID(args["favoritelist"]))

        selected["orderby"] = args["orderby"]
        selected["order"] = args["order"]

        page=1
        if("page" in args and not utils.str_isnullorwhitespace(args["page"])):
            page=int(UUID(args["page"]))

        pagelast = page - 1
        if(pagelast < 1):
            pagelast = 1
        
        pagenext= page + 1

        for stationapi in core.get_stations(selected["name"], selected["country"], selected["language"], selected["tags"], selected["orderby"], False if selected["order"] == "asc" else True, page):
            if(not stationapi.hls):
                if any(stationcore.uuid == UUID(stationapi.stationuuid) for stationcore in selected["favoritelist"].stations):
                    stations.append(RadioStationView(stationapi, True))
                else:
                    stations.append(RadioStationView(stationapi, False))

    return render_template("stationsearch.html",
                               stations=stations, 
                               countries=countries,
                               languages=languages,
                               favorites=core.favorites,
                               selected=selected,
                               pagelast=pagelast,
                               pagenext=pagenext)
    
@app.route("/taglist")
def taglist() -> render_template:
    taglist = core.get_tags()
    return render_template("taglist.html", tags=taglist)

#ajax endpoint
@app.route("/gettags", methods=["POST"])
def gettags() -> render_template:
    form = request.form
    taglist = core.get_tags(form["filter"])
    return render_template("gettags.html", tags=taglist)

#ajax endpoint
@app.route("/changefavorite", methods=["POST"])
def changefavorite() -> None:
    form = request.form
    if(form["changetype"] == "add"):
        core.add_station_to_favlist(UUID(form["stationuuid"]), UUID(form["favlistuuid"]))

    if(form["changetype"] == "remove"):
        core.remove_station_from_favlist(UUID(form["stationuuid"]), UUID(form["favlistuuid"]))

    response = make_response("", 204)
    response.mimetype = "application/json"
    return response

#ajax endpoint
@app.route("/getfavoritelist", methods=["POST"])
def getfavoritelist() -> render_template:
    form = request.form
    favoritlist = core.favorites.getlist(UUID(form["favlistuuid"]))
    stationuuids = [station.uuid for station in favoritlist.stations]
    response = make_response(core.get_serialzeduuids(stationuuids), 200)
    response.mimetype = "application/json"
    return response
