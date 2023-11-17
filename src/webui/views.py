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

        name = None
        if("name" in args and args["name"] and not args["name"].isspace()):
            name=args["name"]

        country = None
        if("country" in args and args["country"] and not args["country"].isspace() and not args["country"]=="nofilter"):
            country=args["country"]
        
        language = None
        if("lang" in args and args["lang"] and not args["lang"].isspace() and not args["lang"]=="nofilter"):
            language=args["lang"]

        tags = []
        if("tags" in args and  args["tags"] and not args["tags"].isspace()):
            print(args["tags"].isspace())
            tags = args["tags"].split(",")

        page=1
        if("page" in args and args["page"] and not args["page"].isspace()):
            page=int(args["page"])

        pagelast = page - 1
        if(pagelast < 1):
            pagelast = 1
        
        pagenext= page + 1

        stations = core.get_stations(name, country, language, tags, args["orderby"], False if args["order"] == "asc" else True, page)

        return render_template("stationsearch.html",
                               stations=stations, 
                               countries=countries,
                               languages=languages,
                               orderby=args["orderby"],
                               order=args["order"],
                               selectedname=name,
                               selectedcountry=country,
                               selectedlang=language,
                               selectedtags=tags,
                               pagelast=pagelast,
                               pagenext=pagenext
                               )
    else:
        return render_template("stationsearch.html",
                               countries=countries,
                               languages=languages,
                               orderby="name",
                               order="asc",
                               selectedname=None,
                               selectedcountry=raspifmsettings.defaulcountry,
                               selectedlang=raspifmsettings.defaultlanguage,
                               selectedtags=[],
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