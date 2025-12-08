from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from core.models.games import Game
from django.urls import reverse
from core.models.saved import SavedGame
from core.recommend.reviews import add_review_1
from core.recommend.likes import toggle_preference
from core.recommend.utils import recommend_next
from core.saved.services import save_game_for_user, remove_game_for_user
from core.search.search import search_games_either

def home(request):
    if request.user.is_authenticated:
        saved_ids = list(request.user.savedgame_set.values_list("game_id", flat=True))
        games = Game.objects.filter(id__in=saved_ids)
    else:
        games = Game.objects.all()[:100]
    return render(request, "home.html", {"games": games})

@login_required
def search_games(request):
    query = request.GET.get("q", "")
    page_number = request.GET.get("page", 1)

    page_obj = search_games_either(query, page_number)

    saved_ids = set()
    if request.user.is_authenticated:
        saved_ids = set(
            SavedGame.objects
            .filter(user=request.user)
            .values_list("game_id", flat=True)
        )

    return render(
        request,
        "search.html",
        {
            "query": query,
            "page_obj": page_obj,
            "games": page_obj.object_list,
            "saved_ids": saved_ids,
        }
    )

@login_required
def recommend_game(request):
    recommendations = recommend_next(request.user)
    if not recommendations:
        return render(request, "recommend.html", {"games": []})
    game_ids = [g.id for g, _ in recommendations]
    games = (
        Game.objects
        .filter(id__in=game_ids)
        .prefetch_related(
            "genres",
            "platforms",
            "developers",
        )
    )
    return render(request, "recommend.html", {"games": games})

@login_required
def vote_game(request, game_id, vote_type):
    if(vote_type == 'like'):
        save_game_for_user(request.user, get_object_or_404(Game, id=game_id))
    return toggle_preference(request, game_id, vote_type)

@login_required
def add_review(request, game_id):
    save_game_for_user(request.user, get_object_or_404(Game, id=game_id))
    return add_review_1(request, game_id)

@login_required
def game_detail(request, game_id):
    game = (
        Game.objects
        .prefetch_related(
            "genres",
            "platforms",
            "developers",
            "likes",
        )
        .get(id=game_id)
    )
    context = game.context_for_user(request.user)
    return render(request, "game_detail.html", context)

@login_required
def add_game(request, game_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    game = get_object_or_404(Game, id=game_id)
    success = save_game_for_user(request.user, game)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "status": "saved" if success else "already_saved",
            "game_id": game.id,
        })
    return redirect(request.META.get("HTTP_REFERER", reverse("core:home")))

@login_required
def remove_game(request, game_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    game = get_object_or_404(Game, id=game_id)
    remove_game_for_user(request.user, game)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "status": "removed",
            "game_id": game.id,
        })
    
    return redirect(request.META.get("HTTP_REFERER", reverse("core:home")))
