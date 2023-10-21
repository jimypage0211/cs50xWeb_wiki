from django.shortcuts import render
import markdown2
from django.http import HttpResponse
from random import randint

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {"entries": util.list_entries()})


def entryPage(request, entryTitle):
    entryStr = ""
    entry = util.get_entry(entryTitle)
    if entry == None:
        entryStr = "None"
    else:
        entryStr = markdown2.markdown(entry)
    return render(
        request,
        "encyclopedia/entryPage.html",
        {"entries": entryStr, "title": entryTitle},
    )


def randomPage(request):
    entries = util.list_entries()
    randEntryName = entries[randint(0, len(entries) - 1)]
    randEntry = markdown2.markdown(util.get_entry(randEntryName))

    return render(
        request,
        "encyclopedia/entryPage.html",
        {"entries": randEntry, "title": randEntryName},
    )
