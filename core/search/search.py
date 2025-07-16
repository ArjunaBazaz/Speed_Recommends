#core/search/search.py
from core.models.games import Game
from django.db.models import Q

def search_games_keyword(query: str):
    qs = Game.objects.filter(
        Q(title__icontains=query) |
        Q(genre__icontains=query) |
        Q(platform__icontains=query)
    ).order_by("title")
    return qs