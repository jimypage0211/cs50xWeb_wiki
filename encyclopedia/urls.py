from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:entryTitle>", views.entryPage, name="getByTitle"),
    path("random", views.randomPage, name= "random" ),   
    path("search", views.searchPage, name="search")
]
