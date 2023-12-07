import traceback
from .web import app
from flask import Response, make_response, render_template, request
from uuid import UUID

from ..core.RaspiFM import RaspiFM
from ..utils import utils
from .ViewProxies.RadioStationView import RadioStationView
from ..core.business.Exceptions import InvalidOperationException
from .ViewProxies.FavoriteListView import FavoriteListView

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
        obj = RaspiFM()
        for favoritelist in RaspiFM().favorites_getlists():
            favoritelists.append(FavoriteListView(favoritelist))

        return render_template("favorites.html",
                               favoritelists=favoritelists,
                               favoritelist=RaspiFM().favorites_getdefaultlist())
    except BaseException as e:
        return get_errorresponse(e)

@app.route("/stationsearch")
def stationsearch() -> str:
    try:
        args = request.args

        stations = []
        countries = RaspiFM().countries_get()
        languages = RaspiFM().languages_get()

        selected = {"name":None, "country":RaspiFM().settings.usersettings.web_defaultcountry, "language":RaspiFM().settings.usersettings.web_defaultlanguage, "tags":[], "orderby":"clickcount", "order":"desc", "favoritelist":RaspiFM().favorites_getdefaultlist() }

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
                selected["favoritelist"] = RaspiFM().favorites_getlist(UUID(args["favoritelist"]))

            selected["orderby"] = args["orderby"]
            selected["order"] = args["order"]

            page=1
            if("page" in args and not utils.str_isnullorwhitespace(args["page"])):
                page=int(args["page"])

            pagelast = page - 1
            if(pagelast < 1):
                pagelast = 1
            
            pagenext= page + 1

            for stationapi in RaspiFM().stations_get(selected["name"], selected["country"], selected["language"], selected["tags"], selected["orderby"], False if selected["order"] == "asc" else True, page):
                if(not stationapi.hls):
                    if any(stationcore.uuid == UUID(stationapi.stationuuid) for stationcore in selected["favoritelist"].stations):
                        stations.append(RadioStationView(stationapi, True))
                    else:
                        stations.append(RadioStationView(stationapi, False))
            
        favoritelists = []
        for favoritelist in RaspiFM().favorites_getlists():
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
        taglist = RaspiFM().tags_get()
        return render_template("taglist.html", tags=taglist)
    except BaseException as e:
        return get_errorresponse(e)

#from here are ajax endpoints:
#ajax
@app.route("/gettags", methods=["POST"])
def gettags() -> str:
    try:
        form = request.form
        taglist = RaspiFM().tags_get(form["filter"])
        return render_template("gettags.html", tags=taglist)
    except BaseException as e:
        return get_errorresponse(e)

#ajax
@app.route("/changefavorite", methods=["POST"])
def changefavorite() -> Response:
    try:
        form = request.form
        if(form["changetype"] == "add"):
            RaspiFM().favorites_add_stationtolist(UUID(form["stationuuid"]), UUID(form["favlistuuid"]))

        if(form["changetype"] == "remove"):
            RaspiFM().favorites_delete_stationfromlist(UUID(form["stationuuid"]), UUID(form["favlistuuid"]))

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
        favoritlist = RaspiFM().favorites_getlist(UUID(form["favlistuuid"]))
        stationuuids = [station.uuid for station in favoritlist.stations]

        response = make_response(RaspiFM().get_serialzeduuids(stationuuids), 200)
        response.mimetype = "application/json"
        return response
    except BaseException as e:
        return get_errorresponse(e)

#ajax
@app.route("/addfavoritelist", methods=["POST"])
def addfavoritelist() -> Response:
    try:
        favoritelist = RaspiFM().favorites_addlist()

        response = make_response(RaspiFM().get_serialzeduuid(favoritelist.uuid), 200)
        response.mimetype = "application/json"
        return response
    except BaseException as e:
        return get_errorresponse(e)

#ajax
@app.route("/changefavoritelist", methods=["POST"])
def changefavoritelist() -> Response:
    try:
        form = request.form
        RaspiFM().favorites_changelistproperty(UUID(form["favlistuuid"]), form["property"], form["value"])
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
        RaspiFM().favorites_deletelist(UUID(form["favlistuuid"]))
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
        favoritelist=RaspiFM().favorites_getlist(UUID(form["favlistuuid"]))
        return render_template("favoritelistcontent.html",
                                favoritelist=favoritelist)
    except BaseException as e:
        return get_errorresponse(e)

def get_errorresponse(e):
    traceback.print_exc() 
    if(isinstance(e, Exception)):
        if(isinstance(e, InvalidOperationException)):
            response = make_response(RaspiFM().get_serialzeddict({"errorNo": 1, "errorType": type(e).__name__, "error": e.args}), 400)
        else:
            response = make_response(RaspiFM().get_serialzeddict({"errorNo": 0, "errorType": type(e).__name__, "error": e.args}), 400)
    else:
        response = make_response(RaspiFM().get_serialzeddict({"errorNo": 0, "errorType": type(e).__name__, "error": e.args}), 500)

    response.mimetype = "application/json"
    return response
