# core/urls.py
from django.urls import path
from . import views
from core.recommend.likes import toggle_preference

urlpatterns = [
    path("recommend/", views.recommend_game, name="recommend_game"),
    path("search/", views.search_games, name="search_games"),
    path("", views.home, name="home"),
    path("game/<int:game_id>/<str:vote_type>/", toggle_preference, name="toggle_game_like")
]