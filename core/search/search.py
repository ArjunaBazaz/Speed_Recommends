#core/search/search.py
from core.models.games import Game
from django.core.paginator import Paginator
from django.db.models import Q

def search_games_either(query: str, page_number: str, selected_genre: str, selected_platform: str):
    return search_games_keyword(query, page_number, selected_genre, selected_platform)

def search_games_keyword(query: str, page_number: str, selected_genre: str, selected_platform: str):
    
    qs = Game.objects.only("id", "title")

    if query:
        qs = qs.filter(
            Q(title__icontains=query) |
            Q(genres__name__icontains=query) |
            Q(platforms__name__icontains=query)
        )

    if selected_genre:
        qs = qs.filter(genres__id=selected_genre)

    if selected_platform:
        qs = qs.filter(platforms__id=selected_platform)

    qs = qs.distinct().order_by("title")

    paginator = Paginator(qs, 100)
    return paginator.get_page(page_number)

def run_ai_search(query: str, user):
    # Placeholder for AI search logic
    # This function should interface with an AI model to get search results
    # For now, it returns an empty list
    return ["placeholder result 1", "placeholder result 2"]