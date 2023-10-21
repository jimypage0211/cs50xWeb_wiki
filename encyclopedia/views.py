from django.shortcuts import render
import markdown2
from django.http import HttpResponse
from random import randint
from django import forms
from . import util


def renderEntryPage(request, entry, entryTitle):
    return render(
        request, "encyclopedia/entryPage.html", {"entries": entry, "title": entryTitle}
    )


def index(request):
    return render(request, "encyclopedia/index.html", {"entries": util.list_entries()})


def entryPage(request, entryTitle):
    entryStr = ""
    entry = util.get_entry(entryTitle)
    if entry == None:
        entryStr = "None"
    else:
        entryStr = markdown2.markdown(entry)
    return renderEntryPage(request,entryStr,entryTitle)


def randomPage(request):
    entries = util.list_entries()
    randEntryName = entries[randint(0, len(entries) - 1)]
    randEntry = markdown2.markdown(util.get_entry(randEntryName))

    return renderEntryPage(request,randEntry,randEntryName)


def searchPage(request):
    if request.method == "POST":
        q = request.POST["q"]
        if util.get_entry(q) == None:
            entry = f'<h1>The requested page for "{q}" was not found.</h1>'
            return renderEntryPage(request,entry,"Error")
        else:
            entry = markdown2.markdown(util.get_entry(q))
            return renderEntryPage(request,entry,q)
    return
