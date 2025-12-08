#core/search/search.py
from core.models.games import Game
from django.core.paginator import Paginator
from django.db.models import Q

def search_games_either(query: str, page_number: str):
    return search_games_keyword(query, page_number)

def search_games_keyword(query: str, page_number: str):
    qs = (
        Game.objects
        .only("id", "title")
        .filter(
            Q(title__icontains=query) |
            Q(genres__name__icontains=query) |
            Q(platforms__name__icontains=query) |
            Q(developers__name__icontains=query)
        )
        .distinct()
        .prefetch_related("genres", "platforms", "developers")
        .order_by("title")
    )

    paginator = Paginator(qs, 100)
    return paginator.get_page(page_number)