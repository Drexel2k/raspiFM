import traceback
from . import app
from flask import Response, make_response, render_template, request
from uuid import UUID

from ..core.raspifmcore import RaspiFM
from ..core import raspifmsettings
from ..utils import utils
from .ViewProxies.RadioStationView import RadioStationView
from ..core.business.Exceptions import InvalidOperationException
from .ViewProxies.FavoriteListView import FavoriteListView

core = RaspiFM()

@app.route("/")
def home() -> str:
    try:
        return render_template("home.html")
    except BaseException as e:
        return get_errorresponse(e)

@app.route("/favorites")
def favorites() -> str:
    try:
        favoritelists = []
        for favoritelist in core.favorites.favoritelists:
            favoritelists.append(FavoriteListView(favoritelist))

        return render_template("favorites.html",
                               favoritelists=favoritelists,
                               favoritelist=core.get_default_favoritelist())
    except BaseException as e:
        return get_errorresponse(e)

@app.route("/stationsearch")
def stationsearch() -> str:
    try:
        args = request.args

        stations = []
        countries = core.get_countries()
        languages = core.get_languages()

        selected = {"name":None, "country":raspifmsettings.defaulcountry, "language":raspifmsettings.defaultlanguage, "tags":[], "orderby":"name", "order":"asc", "favoritelist":core.get_default_favoritelist() }

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
                selected["favoritelist"] = core.get_favoritelist(UUID(args["favoritelist"]))

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
            
        favoritelists = []
        for favoritelist in core.favorites.favoritelists:
            favoritelists.append(FavoriteListView(favoritelist))

        return render_template("stationsearch.html",
                                stations=stations, 
                                countries=countries,
                                languages=languages,
                                favoritelists=favoritelists,
                                selected=selected,
                                pagelast=pagelast,
                                pagenext=pagenext)
    except BaseException as e:
        return get_errorresponse(e)
    
@app.route("/taglist")
def taglist() -> str:
    try:
        taglist = core.get_tags()
        return render_template("taglist.html", tags=taglist)
    except BaseException as e:
        return get_errorresponse(e)

#from here are ajax endpoints:
#ajax
@app.route("/gettags", methods=["POST"])
def gettags() -> str:
    try:
        form = request.form
        taglist = core.get_tags(form["filter"])
        return render_template("gettags.html", tags=taglist)
    except BaseException as e:
        return get_errorresponse(e)

#ajax
@app.route("/changefavorite", methods=["POST"])
def changefavorite() -> Response:
    try:
        form = request.form
        if(form["changetype"] == "add"):
            core.add_station_to_favlist(UUID(form["stationuuid"]), UUID(form["favlistuuid"]))

        if(form["changetype"] == "remove"):
            core.remove_station_from_favlist(UUID(form["stationuuid"]), UUID(form["favlistuuid"]))

        response = make_response("", 204)
        response.mimetype = "application/json"
        return response
    except BaseException as e:
        return get_errorresponse(e)

#ajax
@app.route("/getfavoritelist", methods=["POST"])
def getfavoritelist() -> Response:
    try:
        form = request.form
        favoritlist = core.get_favoritelist(UUID(form["favlistuuid"]))
        stationuuids = [station.uuid for station in favoritlist.stations]

        response = make_response(core.get_serialzeduuids(stationuuids), 200)
        response.mimetype = "application/json"
        return response
    except BaseException as e:
        return get_errorresponse(e)

#ajax
@app.route("/addfavoritelist", methods=["POST"])
def addfavoritelist() -> Response:
    try:
        favoritelist = core.add_favoritelist()

        response = make_response(core.get_serialzeduuid(favoritelist.uuid), 200)
        response.mimetype = "application/json"
        return response
    except BaseException as e:
        return get_errorresponse(e)

#ajax
@app.route("/changefavoritelist", methods=["POST"])
def changefavoritelist() -> Response:
    try:  
        response = make_response("", 204)
        response.mimetype = "application/json"
        return response
    except BaseException as e:
        return get_errorresponse(e)

#ajax
@app.route("/removefavoritelist", methods=["POST"])
def removefavoritelist() -> Response:
    try:
        form = request.form
        core.delete_favoritelist(UUID(form["favlistuuid"]))
        response = make_response("", 204)
        response.mimetype = "application/json"
        return response
    except BaseException as e:
        return get_errorresponse(e)

#ajax
@app.route("/getfavoritelistcontent", methods=["POST"])
def getfavoritelistcontent() -> str:
    try:
        form = request.form
        favoritelist=core.get_favoritelist(UUID(form["favlistuuid"]))
        return render_template("favoritelistcontent.html",
                                favoritelist=favoritelist)
    except BaseException as e:
        return get_errorresponse(e)

def get_errorresponse(e):
    traceback.print_exc() 
    if(isinstance(e, Exception)):
        if(isinstance(e, InvalidOperationException)):
            response = make_response(core.get_serialzeddict({"errorNo": 1, "errorType": type(e).__name__, "error": e.args}), 400)
        else:
            response = make_response(core.get_serialzeddict({"errorNo": 0, "errorType": type(e).__name__, "error": e.args}), 400)
    else:
        response = make_response(core.get_serialzeddict({"errorNo": 0, "errorType": type(e).__name__, "error": e.args}), 500)

    response.mimetype = "application/json"
    return response
