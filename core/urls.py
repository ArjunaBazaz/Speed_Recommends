# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("recommend/", views.recommend_game, name="recommend_game"),
    path("search/", views.search_games, name="search_games"),
]