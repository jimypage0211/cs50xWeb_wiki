from django.shortcuts import render
import markdown2
from django.http import HttpResponse
from random import randint
from django import forms
#from django_markdown.models import MarkdownField
from . import util



class NewEntryForm(forms.Form):
    title = forms.CharField(label='Entry name')
    markdown = forms.CharField(label='')
    markdown.widget= forms.Textarea()
    markdown.initial = "Enter markdown for entry here"

# Helper method to render an entryPage
def renderEntryPage(request, entry, entryTitle):
    return render(
        request, "encyclopedia/entryPage.html", {"entries": entry, "title": entryTitle}
    )


# Helper method to render an list of entries
def renderLists(request, list):
    return render(request, "encyclopedia/index.html", {"entries": list})


# Helper method to check if the entry query is a substring of a saved entry
def isSubstringOfEntry(newEntry):
    entries = util.list_entries()
    matches = []
    # Check if substring
    for savedEntry in entries:
        if newEntry.upper() in savedEntry.upper():
            matches.append(savedEntry)
    if len(matches) == 0:
        return None
    else:
        return matches


def index(request):
    return renderLists(request, util.list_entries())


def entryPage(request, entryTitle):
    entryStr = ""
    entry = util.get_entry(entryTitle)
    if entry == None:
        entryStr = f'<h1>The requested page for "{entryTitle}" was not found.</h1>'
        entryTitle = "Error"
    else:
        entryStr = markdown2.markdown(entry)
    return renderEntryPage(request, entryStr, entryTitle)


def randomPage(request):
    entries = util.list_entries()
    randEntryName = entries[randint(0, len(entries) - 1)]
    randEntry = markdown2.markdown(util.get_entry(randEntryName))

    return renderEntryPage(request, randEntry, randEntryName)


def searchPage(request):
    if request.method == "POST":
        q = request.POST["q"]
        if util.get_entry(q) == None:
            matches = isSubstringOfEntry(q)
            if matches == None:
                entry = f'<h1>The requested page for "{q}" was not found.</h1>'
                return renderEntryPage(request, entry, "Error")
            else:
                return renderLists(request, matches)

        else:
            entry = markdown2.markdown(util.get_entry(q))
            return renderEntryPage(request, entry, q)
    return


def newEntry(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid:
            title = form.data["title"]
            markdown = form.data["markdown"]
            util.save_entry(title,markdown)
            return render(request, "encyclopedia/newEntryPage.html", {"form": NewEntryForm()})  
        else:
            return HttpResponse("form is not valid")
    else:
        return render(request, "encyclopedia/newEntryPage.html", {"form": NewEntryForm()})
    