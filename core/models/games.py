from django.conf import settings
from django.db import models
from core.models.reviews import Likes

class Game(models.Model):
    title = models.CharField(max_length=200, verbose_name="Game Title")
    genre = models.CharField(max_length=100, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    release_date = models.DateField(null=True, blank=True)
    platform = models.CharField(max_length=100, db_index=True)

    # Many-to-many with through model to hold votes
    preferences = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Preference',
        related_name='preferred_games'
    )

    @property
    def likes_count(self):
        return self.preference_set.filter(vote=Likes.LIKE).count()

    @property
    def dislikes_count(self):
        return self.preference_set.filter(vote=Likes.DISLIKE).count()

    def user_vote(self, user):
        pref = self.preference_set.filter(user=user).first()
        return pref.vote if pref else None

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title", "platform", "release_date"]
        indexes = [
            models.Index(fields=["genre", "release_date"]),
        ]

    def context_for_user(self, user):
        """Return a dict of everything templates need for this game."""
        user_pref = self.preference_set.filter(user=user).first()
        user_review = self.review_set.filter(user=user).first()
        other_reviews = self.review_set.exclude(user=user)

        return {
            "game": self,
            "user_pref": user_pref,
            "user_review": user_review,
            "reviews": other_reviews,
        }