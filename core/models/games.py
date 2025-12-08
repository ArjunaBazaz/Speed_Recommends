from django.conf import settings
from django.db import models
from core.models.reviews import Likes
from core.models.game_info import Genre, Platform, Developer

class Game(models.Model):
    title = models.CharField(max_length=200, verbose_name="Game Title")
    genres = models.ManyToManyField(Genre, related_name="games")
    developers = models.ManyToManyField(Developer, related_name="games")
    platforms = models.ManyToManyField(Platform, related_name="games")
    release_date = models.DateField(null=True, blank=True)
    release_year = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    baseline_score = models.FloatField(default=0.0)

    # Many-to-many with through model to hold votes
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='core.Likes',
        related_name='liked_games'
    )

    @property
    def likes_count(self):
        return Likes.objects.filter(game=self, vote=Likes.LIKE).count()

    @property
    def dislikes_count(self):
        return Likes.objects.filter(game=self, vote=Likes.DISLIKE).count()

    def user_vote(self, user):
        pref = Likes.objects.filter(user=user, game=self).first()
        return pref.vote if pref else None

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title", "release_year", "release_date", "baseline_score"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["release_year"]),
            models.Index(fields=["baseline_score"]),
        ]

    def context_for_user(self, user):
        """
        Return a dict of everything templates need for this game.
        Includes genres and platforms for display.
        """

        user_pref = None
        user_review = None

        if user and user.is_authenticated:
            user_pref = Likes.objects.filter(user=user, game=self).first()

            if hasattr(self, "reviews"):
                user_review = self.reviews.filter(user=user).first()

        other_reviews = (
            self.reviews.exclude(user=user)
            if hasattr(self, "reviews") and user and user.is_authenticated
            else self.reviews.all()
            if hasattr(self, "reviews")
            else []
        )

        return {
            "game": self,
            "user_pref": user_pref,
            "user_review": user_review,
            "reviews": other_reviews,
            "likes_count": self.likes_count,
            "dislikes_count": self.dislikes_count,
            "genres": self.genres.all(),
            "platforms": self.platforms.all(),
            "developers": self.developers.all(),
        }
