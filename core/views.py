from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from core.models.games import Game
from core.recommend.reviews import add_review_1
from core.recommend.likes import toggle_preference
from core.recommend.utils import recommend_next
from core.saved.services import save_game_for_user, remove_game_for_user
from core.search.search import search_games_keyword

def home(request):
    if request.user.is_authenticated:
        saved_ids = request.user.savedgame_set.values_list("game_id", flat=True)
        saved_games = Game.objects.filter(id__in=saved_ids)
        other_games = Game.objects.exclude(id__in=saved_ids)
        games = list(saved_games) + list(other_games)  # saved first
    else:
        games = Game.objects.all()
    return render(request, "home.html", {"games": games})

@login_required
def search_games(request):
    q = request.GET.get("q", "")
    games = search_games_keyword(q)
    return render(request, "search.html", {"games": games, "query": q})

@login_required
def recommend_game(request):
    recommendations = recommend_next(request.user)
    games = [g for g, _ in recommendations] if recommendations else []
    return render(request, "recommend.html", {"games": games})

@login_required
def vote_game(request, game_id, vote_type):
    return toggle_preference(request, game_id, vote_type)

@login_required
def add_review(request, game_id):
    return add_review_1(request, game_id)

@login_required
def game_detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    ctx = game.context_for_user(request.user)
    return render(request, "game_detail.html", ctx)

@login_required
def add_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    save_game_for_user(request.user, game)
    return redirect(request.META.get("HTTP_REFERER", "core:home"))

@login_required
def remove_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    remove_game_for_user(request.user, game)
    return redirect(request.META.get("HTTP_REFERER", "core:home"))
