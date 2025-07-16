# core/saved/services.py
from django.db import IntegrityError

from core.models.games import Game
from core.models.saved import SavedGame


def save_game_for_user(user, game: Game) -> bool:
    try:
        SavedGame.objects.create(user=user, game=game)
        return True
    except IntegrityError:
        # UniqueConstraint in SavedGame.Meta guarantees one row per pair
        return False


def remove_game_for_user(user, game: Game) -> None:
    SavedGame.objects.filter(user=user, game=game).delete()
