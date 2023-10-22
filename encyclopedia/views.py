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
    title = forms.CharField(label="Entry name")
    markdown = forms.CharField(label="")
    placeholder = "#Enter the content markup for this entry here ..."
    markdown.widget = forms.Textarea(attrs={"placeholder": placeholder})


def renderExistError(request, title):
    error = f'<h1>The requested page for "{title}" alreadyExist.</h1>'
    return render(
        request,
        "encyclopedia/errorPage.html",
        {"errorMsg": error, "errorType": "Page already exist"},
    )


def renderNotFoundError(request, title):
    error = f'<h1>The requested page for "{title}" was not found.</h1>'
    return render(
        request,
        "encyclopedia/errorPage.html",
        {"errorMsg": error, "errorType": "Page not found"},
    )


def delete_entry(title):
    """
    Deletes an encyclopedia entry, by its title. If no such
    entry exists, the function returns None.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)


# Helper method to render an entryPage
def renderEntryPage(request, entry, entryTitle):
    return render(
        request,
        "encyclopedia/entryPage.html",
        {"entries": entry, "entryTitle": entryTitle},
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
        return renderNotFoundError(request, entryTitle)
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
    return


def newEntry(request):
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
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid:
            newTitle = form.data["title"]
            markdown = form.data["markdown"]
            # Save the new edited entry
            util.save_entry(newTitle, markdown)
            # delete previous entry
            if newTitle != entryTitle:
                delete_entry(entryTitle)
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
    """
    Deletes an encyclopedia entry, by its title. If no such
    entry exists, the function returns None.
    """
    filename = f"entries/{entryTitle}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    return renderLists(request, util.list_entries)
