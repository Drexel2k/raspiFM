from flask import render_template, request
from . import app
from ..core.raspifmcore import RaspiFM
from ..core import raspifmsettings
from ..utils import utils

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

    countries = core.get_countries()
    languages = core.get_languages()

    selected = {"name":None, "country":raspifmsettings.defaulcountry, "language":raspifmsettings.defaultlanguage, "tags":[], "orderby":"name", "order":"asc" }

    if args:
        if("name" in args and not utils.str_isnullorwhitespace(args["name"])):
            selected["name"]=args["name"]

        if("country" in args and not utils.str_isnullorwhitespace(args["country"]) and not args["country"]=="nofilter"):
            selected["country"]=args["country"]
        
        if("lang" in args and not utils.str_isnullorwhitespace(args["lang"]) and not args["lang"]=="nofilter"):
            selected["language"]=args["lang"]

        if("tags" in args and not utils.str_isnullorwhitespace(args["tags"])):
            print(args["tags"].isspace())
            selected["tags"] = args["tags"].split(",")

        selected["orderby"] = args["orderby"]
        selected["order"] = args["order"]

        page=1
        if("page" in args and not utils.str_isnullorwhitespace(args["page"])):
            page=int(args["page"])

        pagelast = page - 1
        if(pagelast < 1):
            pagelast = 1
        
        pagenext= page + 1

        stations = core.get_stations(selected["name"], selected["country"], selected["language"], selected["tags"], selected["orderby"], False if selected["order"] == "asc" else True, page)

        return render_template("stationsearch.html",
                               stations=stations, 
                               countries=countries,
                               languages=languages,
                               selected=selected,
                               pagelast=pagelast,
                               pagenext=pagenext
                               )
    else:
        return render_template("stationsearch.html",
                               countries=countries,
                               languages=languages,
                               selected=selected,
                               pagelast=1,
                               pagenext=2
                               )
    
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