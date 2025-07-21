from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from core.models.games import Game
from django.http import HttpResponseNotAllowed
from core.recommend.reviews import add_review_1
from core.recommend.likes import toggle_preference
from core.recommend.utils import recommend_next
from core.saved.services import save_game_for_user, remove_game_for_user
from core.search.search import search_games_keyword

def home(request):
    if request.user.is_authenticated:
        saved_ids = list(request.user.savedgame_set.values_list("game_id", flat=True))
        print(f"Saved game IDs for user {request.user}: {saved_ids}", flush=True)
        games = Game.objects.filter(id__in=saved_ids)
        print(f"Games queryset count: {games.count()}", flush=True)
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
    print(f"Method Vote Game: {request.method} for game_id {game_id} of vote type {vote_type}", flush=True)
    if(vote_type == 'like'):
        save_game_for_user(request.user, get_object_or_404(Game, id=game_id))
    return toggle_preference(request, game_id, vote_type)

@login_required
def add_review(request, game_id):
    print(f"Method Add Review: {request.method} for game_id {game_id}", flush=True)
    save_game_for_user(request.user, get_object_or_404(Game, id=game_id))
    return add_review_1(request, game_id)

@login_required
def game_detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    ctx = game.context_for_user(request.user)
    return render(request, "game_detail.html", ctx)

@login_required
def add_game(request, game_id):
    print(f"Method Add Game: {request.method} for game_id {game_id}", flush=True)
    if request.method == "POST":
        game = get_object_or_404(Game, id=game_id)
        success = save_game_for_user(request.user, game)
        print(f"Saved game? {success}", flush=True)
        return redirect(request.META.get("HTTP_REFERER", "core:home"))
    else:
        return HttpResponseNotAllowed(['POST'])

@login_required
def remove_game(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    remove_game_for_user(request.user, game)
    return redirect(request.META.get("HTTP_REFERER", "core:home"))
