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
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='core.Likes',
        related_name='liked_games'
    )

    @property
    def likes_count(self):
        return self.likes.filter(vote=Likes.LIKE).count()

    @property
    def dislikes_count(self):
        return self.likes.filter(vote=Likes.DISLIKE).count()

    def user_vote(self, user):
        pref = Likes.objects.filter(user=user, game=self).first()
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
        user_pref = Likes.objects.filter(user=user, game=self).first()
        user_review = self.reviews.filter(user=user).first()
        other_reviews = self.reviews.exclude(user=user)

        return {
            "game": self,
            "user_pref": user_pref,
            "user_review": user_review,
            "reviews": other_reviews,
        }