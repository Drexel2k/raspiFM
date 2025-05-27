import traceback

from common.Exceptions.InvalidOperationError import InvalidOperationError
from webui.run import app
from flask import Response, make_response, render_template, request

from common import utils
from common import json
from common.json import UUIDEncoder
from common.socket.raspifm_client.RaspiFMProxy import RaspiFMProxy
from webui.ViewProxies.FavoriteListView import FavoriteListView
from webui.ViewProxies.RadioStationView import RadioStationView
from common.Exceptions.RadioBrowserApiError import RadioBrowserApiError

@app.route("/")
def home() -> str:
    try:
        return render_template("home.html")
    except BaseException as e:
        return get_error_response(e)

@app.route("/favorites")
def favorites() -> str:
    try:
        favoritelists = []
        for favoritelist in sorted(RaspiFMProxy().favorites_getlists(), key=lambda favlistinternal: favlistinternal["displayorder"]):
            favoritelists.append(FavoriteListView(favoritelist))

        return render_template("favorites.html",
                               favoritelists=favoritelists,
                               favoritelist=RaspiFMProxy().favorites_getdefaultlist())
    except (RadioBrowserApiError):
        return render_template("radiobrowser_api_error.html", route="favorites")
    except (ConnectionRefusedError, FileNotFoundError):
        return render_template("raspifm_service_not_available.html", route="favorites") 
    except BaseException as e:
        return get_error_response(e)

@app.route("/stationsearch")
def stationsearch() -> str:
    try:
        args = request.args

        stations = []
        countries = RaspiFMProxy().countries_get()
        languages = RaspiFMProxy().languages_get()

        selected = {"name":None, "country":RaspiFMProxy().settings_web_defaultcountry(), "language":RaspiFMProxy().settings_web_defaultlanguage(), "tags":[], "orderby":"clickcount", "order":"desc", "favoritelist":RaspiFMProxy().favorites_getdefaultlist() }

        pagelast=1
        pagenext=2

        if not args is None and len(args) > 0:
            if "name" in args and not utils.str_isnullorwhitespace(args["name"]):
                selected["name"]=args["name"]

            if "country" in args and not utils.str_isnullorwhitespace(args["country"]):
                selected["country"]=args["country"]
            
            if "lang" in args and not utils.str_isnullorwhitespace(args["lang"]):
                selected["language"]=args["lang"]

            if "tags" in args and not utils.str_isnullorwhitespace(args["tags"]):
                selected["tags"] = args["tags"].split(",")

            if "favoritelist" in args and not utils.str_isnullorwhitespace(args["favoritelist"]):
                selected["favoritelist"] = RaspiFMProxy().favorites_getlist(args["favoritelist"])

            selected["orderby"] = args["orderby"]
            selected["order"] = args["order"]

            page=1
            if "page" in args and not utils.str_isnullorwhitespace(args["page"]):
                page=int(args["page"])

            pagelast = page - 1
            if pagelast < 1:
                pagelast = 1
            
            pagenext= page + 1

            country = selected["country"] if selected["country"] != "nofilter" else None

            language = selected["language"] if selected["language"] != "nofilter" else None

            for stationapi in RaspiFMProxy().stationapis_get(selected["name"], country, language, selected["tags"], selected["orderby"], False if selected["order"] == "asc" else True, page):
                if stationapi["hls"] == 0:
                    if any(stationcoreentry["radiostation"]["uuid"] == stationapi["stationuuid"] for stationcoreentry in selected["favoritelist"]["stations"]):
                        stations.append(RadioStationView(stationapi, True))
                    else:
                        stations.append(RadioStationView(stationapi, False))

        favoritelists = []
        for favoritelist in sorted(RaspiFMProxy().favorites_getlists(), key=lambda favlistinternal: favlistinternal["displayorder"]):
            favoritelists.append(FavoriteListView(favoritelist))

        return render_template("stationsearch.html",
                                stations=stations, 
                                countries=countries,
                                languages=languages,
                                favoritelists=favoritelists,
                                selected=selected,
                                pagelast=pagelast,
                                pagenext=pagenext)
#    except (RadioBrowserApiError):
#        return render_template("radiobrowser_api_error.html", route="stationsearch", current_args=args)
    except (ConnectionRefusedError, FileNotFoundError):
        return render_template("raspifm_service_not_available.html", route="stationsearch")
    except BaseException as e:
        return get_error_response(e)
    
@app.route("/taglist")
def taglist() -> str:
    try:
        taglist = RaspiFMProxy().tags_get()
        return render_template("taglist.html", tags=taglist)
    except (RadioBrowserApiError):
        return render_template("radiobrowser_api_error.html", route="taglist")
    except (ConnectionRefusedError, FileNotFoundError):
        return render_template("raspifm_service_not_available.html", route="taglist") 
    except BaseException as e:
        return get_error_response(e)
    
@app.route("/settings")
def settings() -> str:
    try:
        countries = RaspiFMProxy().countries_get()
        languages = RaspiFMProxy().languages_get()

        selected = {"country":RaspiFMProxy().settings_web_defaultcountry(), "language":RaspiFMProxy().settings_web_defaultlanguage()}

        return render_template("settings.html",
                                countries=countries,
                                languages=languages,
                                selected=selected)
    except (ConnectionRefusedError, FileNotFoundError):
        return render_template("raspifm_service_not_available.html", route="settings") 
    except BaseException as e:
        return get_error_response(e)

#from here are ajax endpoints:
#ajax
@app.route("/gettags", methods=["POST"])
def gettags() -> str:
    try:
        form = request.form
        taglist = RaspiFMProxy().tags_get(form["filter"])
        return render_template("gettags.html", tags=taglist)
    except BaseException as e:
        return get_error_response(e)

#ajax
@app.route("/changefavorite", methods=["POST"])
def changefavorite() -> Response:
    try:
        form = request.form
        if form["changetype"] == "add":
            RaspiFMProxy().favorites_add_stationtolist(form["stationuuid"], form["favlistuuid"])

        if form["changetype"] == "remove":
            RaspiFMProxy().favorites_remove_stationfromlist(form["stationuuid"], form["favlistuuid"])

        response = make_response("", 204)
        response.mimetype = "application/json"
        return response
    except BaseException as e:
        return get_error_response(e)

#ajax
@app.route("/getfavoritelist", methods=["POST"])
def getfavoritelist() -> Response:
    try:
        form = request.form
        favoritlist = RaspiFMProxy().favorites_getlist(form["favlistuuid"])
        stationuuids = [stationentry["radiostation"]["uuid"] for stationentry in favoritlist["stations"]]

        response = make_response(stationuuids, 200)
        response.mimetype = "application/json"
        return response
    except BaseException as e:
        return get_error_response(e)

#ajax
@app.route("/addfavoritelist", methods=["POST"])
def addfavoritelist() -> Response:
    try:
        favoritelist = RaspiFMProxy().favorites_addlist()

        response = make_response(json.serialize_to_string_or_bytes(favoritelist["uuid"]), 200)
        response.mimetype = "application/json"
        return response
    except BaseException as e:
        return get_error_response(e)

#ajax
@app.route("/changefavoritelist", methods=["POST"])
def changefavoritelist() -> Response:
    try:
        form = request.form
        RaspiFMProxy().favorites_changelistproperty(form["favlistuuid"], form["property"], form["value"])
        response = make_response("", 204)
        response.mimetype = "application/json"
        return response
    except BaseException as e:
        return get_error_response(e)

#ajax
@app.route("/deletefavoritelist", methods=["POST"])
def deletefavoritelist() -> Response:
    try:
        form = request.form
        RaspiFMProxy().favorites_deletelist(form["favlistuuid"])
        response = make_response("", 204)
        response.mimetype = "application/json"
        return response
    except BaseException as e:
        return get_error_response(e)

#ajax
@app.route("/getfavoritelistcontent", methods=["POST"])
def getfavoritelistcontent() -> str:
    try:
        form = request.form
        favoritelist=RaspiFMProxy().favorites_getlist(form["favlistuuid"])
        return render_template("favoritelistcontent.html",
                                favoritelist=favoritelist)
    except BaseException as e:
        return get_error_response(e)
    
#ajax
@app.route("/movefavoritelist", methods=["POST"])
def movefavoritelist() -> Response:
    try:
        form = request.form
        RaspiFMProxy().favorites_movelist(form["favlistuuid"], form["direction"])
        response = make_response("", 204)
        response.mimetype = "application/json"
        return response
    except BaseException as e:
        return get_error_response(e)

#ajax
@app.route("/movestationinfavoritelist", methods=["POST"])
def movestationinfavoritelist() -> Response:
    try:
        form = request.form
        RaspiFMProxy().favorites_move_station_in_list(form["favlistuuid"], form["stationuuid"], form["direction"])
        response = make_response("", 204)
        response.mimetype = "application/json"
        return response
    except BaseException as e:
        return get_error_response(e)
    
#ajax
@app.route("/changesettings", methods=["POST"])
def changesettings() -> Response:
    try:
        form = request.form
        RaspiFMProxy().settings_changeproperty(form["property"], form["value"])
        response = make_response("", 204)
        response.mimetype = "application/json"
        return response
    except BaseException as e:
        return get_error_response(e)

def get_error_response(e):
    #errorNo is uses in JavaScript to show more helpful error messages
    if isinstance(e, RadioBrowserApiError):
        traceback.print_exc() 
        response = make_response(json.serialize_to_string_or_bytes({"errorNo": 2, "errorType": type(e).__name__, "error": e.additional_info_message}, encoder=UUIDEncoder), 500)
    elif isinstance(e, InvalidOperationError):
        response = make_response(json.serialize_to_string_or_bytes({"errorNo": 1, "errorType": type(e).__name__, "error": e.additional_info_message}, encoder=UUIDEncoder), 422)
    else:
        traceback.print_exc() 
        response = make_response(json.serialize_to_string_or_bytes({"errorNo": 0, "errorType": type(e).__name__, "error": e.args}, encoder=UUIDEncoder), 500)

    response.mimetype = "application/json"
    return response
