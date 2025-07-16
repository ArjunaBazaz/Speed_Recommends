# core/models/saved.py   (new file)
from django.conf import settings
from django.db import models
from core.models.games import Game

class SavedGame(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="saved_by")
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "game"],
                name="unique_saved_game",
            )
        ]

    def __str__(self):
        return f"{self.user} saved {self.game}"
