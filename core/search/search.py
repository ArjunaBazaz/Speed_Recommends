#core/search/search.py
from core.models.games import Game
from django.core.paginator import Paginator
from django.db.models import Q

def search_games_keyword(query: str, page_number: str, selected_genres: str, selected_platforms: str):

    qs = Game.objects.only("id", "title")

    if query:
        qs = qs.filter(
            Q(title__icontains=query) |
            Q(genres__name__icontains=query) |
            Q(platforms__name__icontains=query)
        )

    if selected_genres:
        qs = qs.filter(genres__id__in=selected_genres)

    if selected_platforms:
        qs = qs.filter(platforms__id__in=selected_platforms)

    qs = qs.distinct().order_by("title")

    paginator = Paginator(qs, 100)
    return paginator.get_page(page_number)