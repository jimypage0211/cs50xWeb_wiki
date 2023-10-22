from django.shortcuts import render
from django.urls import reverse
import markdown2
from django.http import HttpResponse, HttpResponseRedirect
from random import randint
from django import forms
from django.core.files.storage import default_storage

# from django_markdown.models import MarkdownField
from . import util


class NewEntryForm(forms.Form):
    """Create and Edit form class"""

    title = forms.CharField(label="Entry name")
    markdown = forms.CharField(label="")
    placeholder = "#Enter the content markup for this entry here ..."
    markdown.widget = forms.Textarea(attrs={"placeholder": placeholder})


def renderExistError(request, title):
    """Helper function to render the already exist error page"""

    error = f'<h1>The requested page for "{title}" alreadyExist.</h1>'
    return render(
        request,
        "encyclopedia/errorPage.html",
        {"errorMsg": error, "errorType": "Page already exist"},
    )


def renderNotFoundError(request, title):
    """Helper function to render the not found error page"""

    error = f'<h1>The requested page for "{title}" was not found.</h1>'
    return render(
        request,
        "encyclopedia/errorPage.html",
        {"errorMsg": error, "errorType": "Page not found"},
    )


def renderEntryPage(request, entry, entryTitle):
    """Helper method to render an entryPage"""

    return render(
        request,
        "encyclopedia/entryPage.html",
        {"entries": entry, "entryTitle": entryTitle},
    )


def renderLists(request, list):
    """Helper method to render an list of entries"""
    return render(request, "encyclopedia/index.html", {"entries": list})


#
def isSubstringOfEntry(newEntry):
    """Helper method to check if the entry query is a substring of a saved entry"""

    entries = util.list_entries()
    matches = []
    for savedEntry in entries:
        if newEntry.upper() in savedEntry.upper():
            matches.append(savedEntry)
    if len(matches) == 0:
        return None
    else:
        return matches


def index(request):
    """Renders Home page"""

    return renderLists(request, util.list_entries())


def entryPage(request, entryTitle):
    """Renders requested entry page or error if not found"""
    entryStr = ""
    entry = util.get_entry(entryTitle)
    if entry == None:
        return renderNotFoundError(request, entryTitle)
    else:
        content = markdown2.markdown(entry)
    return renderEntryPage(request, content, entryTitle)


def randomPage(request):
    """Renders a random entry page"""

    entries = util.list_entries()
    randEntryName = entries[randint(0, len(entries) - 1)]
    randEntry = markdown2.markdown(util.get_entry(randEntryName))
    return renderEntryPage(request, randEntry, randEntryName)


def searchPage(request):
    """Renders the list of substrings matches from the search"""

    if request.method == "POST":
        entryTitle = request.POST["q"]
        if util.get_entry(entryTitle) == None:
            matches = isSubstringOfEntry(entryTitle)
            if matches == None:
                return renderNotFoundError(request, entryTitle)
            else:
                return renderLists(request, matches)
        else:
            entry = markdown2.markdown(util.get_entry(entryTitle))
            return renderEntryPage(request, entry, entryTitle)
    return HttpResponse("Something didn't work")


def newEntry(request):
    """
    Renders the NEW entry page. If page already exist renders 
    an already exist error otherwise it renders the new entry page
    """

    if request.method == "POST":
        # we are receiving a form submitted
        form = NewEntryForm(request.POST)
        if form.is_valid:
            title = form.data["title"]
            markdown = form.data["markdown"]
            # If entry exist in files render error page.
            if util.get_entry(title) != None:
                return renderExistError(request, title)
            else:
                # Save the entry.
                util.save_entry(title, markdown)
                # Go to the fresh created entry page.
                return HttpResponseRedirect(
                    reverse("getByTitle", kwargs={"entryTitle": title})
                )
        else:
            return HttpResponse("form is not valid")
    else:
        # Goes to the create new entry page.
        return render(
            request, "encyclopedia/newEntryPage.html", {"form": NewEntryForm()}
        )


def editEntry(request, entryTitle):
    """
    Renders the EDIT entry page. If title doesnt change, it renders the edited entry,
    otherwise, it deletes the entry with the previous name and renders all entries
    """
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid:
            newTitle = form.data["title"]
            markdown = form.data["markdown"]
            # Save the new edited entry
            util.save_entry(newTitle, markdown)
            # delete previous entry
            if newTitle != entryTitle:
                deleteEntry(request, entryTitle)
            # Go to the fresh create entry page
            return HttpResponseRedirect(
                reverse("getByTitle", kwargs={"entryTitle": newTitle})
            )
        return
    else:
        entry = util.get_entry(entryTitle)
        form = NewEntryForm(initial={"title": entryTitle, "markdown": entry})
        return render(
            request,
            "encyclopedia/editEntryPage.html",
            {"form": form, "entryTitle": entryTitle},
        )


def deleteEntry(request, entryTitle):
    """ Deletes an encyclopedia entry, by its title. Renders all entries"""

    filename = f"entries/{entryTitle}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    return renderLists(request, util.list_entries)

