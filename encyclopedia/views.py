from django.shortcuts import render
import markdown2
from django.http import HttpResponse

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {"entries": util.list_entries()})


def entryUrl(request, entryTitle):
    entryStr = ""
    entry = util.get_entry(entryTitle)
    if entry == None:
        entryStr = "None"
    else:
        entryStr = markdown2.markdown(entry)
    return render(
        request,
        "encyclopedia/getByTitle.html",
        {"entries": entryStr, "title": entryTitle},
    )
