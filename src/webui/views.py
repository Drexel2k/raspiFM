from flask import render_template, request
from . import app
from ..core.raspifmcore import RaspiFM
from ..core import raspifmsettings

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

    if args:
        #prevlink = 
        #nextlink=

        name = args["name"]
        if(name==""):
            name=None

        country = args["country"]
        if(country=="nofilter"):
            country=None

        language = args["lang"]
        if(language=="nofilter"):
            language=None
        
        tags = args["tags"]
        if(not tags):
            tags=None

        tags = tags.split(",")

        stations = core.get_stations(name, country, language, tags, args["orderby"], False if args["order"] == "asc" else True)

        return render_template("stationsearch.html",
                               stations=stations, 
                               countries=countries,
                               languages=languages,
                               args=args)
    else:
        args = { "country": raspifmsettings.defaulcountry, "lang" : raspifmsettings.defaultlanguage}

        return render_template("stationsearch.html",
                               countries=countries,
                               languages=languages,
                               args=args)
    
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