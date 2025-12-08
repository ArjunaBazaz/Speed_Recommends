#core/search/search.py
from core.models.games import Game
from django.db.models import Q

def search_games_either(query: str):
    return search_games_keyword(query)

def search_games_keyword(query: str):
    qs = (
        Game.objects
        .filter(
            Q(title__icontains=query) |
            Q(genres__name__icontains=query) |
            Q(platforms__name__icontains=query) |
            Q(developers__name__icontains=query)
        )
        .distinct()
        .prefetch_related(
            "genres",
            "platforms",
            "developers",
        )
        .order_by("title")
    )

    return qs[:100]