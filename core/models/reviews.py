from django.conf import settings
from django.db import models

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey("core.Game", on_delete=models.CASCADE, related_name="reviews")
    reviewTime = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Score(models.TextChoices):
        ZERO = "1", "0"
        ONE = "2", "1"
        TWO = "3", "2"
        THREE = "4", "3"
        FOUR = "5", "4"
        FIVE = "6", "5"
        SIX = "7", "6"
        SEVEN = "8", "7"
        EIGHT = "9", "8"
        NINE = "10", "9"
        TEN = "11", "10"

    score = models.CharField(max_length=2, choices=Score.choices, default=Score.FIVE)
    text = models.TextField(blank=True)

    def __str__(self):
        return self.text

    def update_review(self, new_score, new_text):
        self.text = new_text
        self.score = new_score
        self.save()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

class Likes(models.Model):
    LIKE = 1
    DISLIKE = -1
    VOTES = ((DISLIKE, "Dislike"), (LIKE, "Like"))

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey("core.Game", on_delete=models.CASCADE, related_name="likes_set")
    vote = models.SmallIntegerField(choices=VOTES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "game"], name="unique_pref"),
        ]

