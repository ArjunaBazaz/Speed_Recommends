from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from core.models.games import Game
from django.urls import reverse
from core.models.saved import SavedGame
from core.models.reviews import Review
from core.recommend.reviews import add_review_1
from core.recommend.likes import toggle_preference
from core.recommend.utils import recommend_next
from core.saved.services import save_game_for_user, remove_game_for_user
from core.search.search import search_games_keyword
from core.ai.interpret import interpret_prompt_to_spec
from core.ai.execute import run_spec
from core.models.game_info import Genre, Platform
from django.core.paginator import Paginator
from django.db.models import Q
from urllib.parse import urlencode

def home(request):
    if request.user.is_authenticated:
        user = request.user

        reviewed_games = (
            Review.objects
            .filter(user=user)
            .select_related("game")
            .values_list("game_id", flat=True)
        )

        played_games = (
            SavedGame.objects
            .filter(user=user, game_id__in=reviewed_games)
            .select_related("game")
        )

        saved_games = (
            SavedGame.objects
            .filter(user=user)
            .exclude(game_id__in=reviewed_games)
            .select_related("game")
        )

        return render(
            request,
            "home.html",
            {
                "played_games": played_games,
                "saved_games": saved_games,
            }
        )
    else:
        return render(request, "home.html", {"games": Game.objects.all()[:100]})

@login_required
def ai_search(request):
    prompt = ""
    spec = None
    results = []
    error = None

    saved_ids = set(
        SavedGame.objects
        .filter(user=request.user)
        .values_list("game_id", flat=True)
    )

    if request.method == "POST":
        prompt = (request.POST.get("prompt") or "").strip()
        if not prompt:
            error = "Please enter a prompt."
        else:
            spec = interpret_prompt_to_spec(prompt)
            results = list(run_spec(spec))

    return render(request, "ai_search.html", {
        "prompt": prompt,
        "spec": spec,
        "results": results,
        "error": error,
        "saved_ids": saved_ids,
    })

@login_required
def search_games(request):

    query = request.GET.get("q", "")
    page_number = request.GET.get("page", 1)

    selected_genres = request.GET.getlist("genres")
    selected_platforms = request.GET.getlist("platforms")

    page_obj = search_games_keyword(
        query,
        page_number,
        selected_genres,
        selected_platforms,
    )

    saved_ids = set(
        SavedGame.objects
        .filter(user=request.user)
        .values_list("game_id", flat=True)
    )

    all_genres = Genre.objects.order_by("name")
    all_platforms = Platform.objects.order_by("name")

    preserved = request.GET.copy()
    if "page" in preserved:
        preserved.pop("page")

    preserved_query = preserved.urlencode()

    return render(
        request,
        "search.html",
        {
            "query": query,
            "games": page_obj.object_list,
            "page_obj": page_obj,
            "saved_ids": saved_ids,
            "genres": all_genres,
            "platforms": all_platforms,
            "selected_genres": selected_genres,
            "selected_platforms": selected_platforms,
            "preserved_query": preserved_query,
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
