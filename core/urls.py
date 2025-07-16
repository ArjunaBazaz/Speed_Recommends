# core/urls.py
from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("recommend/", views.recommend_game, name="recommend_game"),
    path("search/", views.search_games, name="search_games"),
    path("", views.home, name="home"),
    path("game/<int:game_id>/<str:vote_type>/", views.vote_game, name="toggle_game_like"),
    path('game/<int:game_id>/review/', views.add_review, name='add_review'),
    path("game/<int:game_id>/save/", views.add_game,   name="save_game"),
    path("game/<int:game_id>/unsave/", views.remove_game, name="unsave_game"),
]