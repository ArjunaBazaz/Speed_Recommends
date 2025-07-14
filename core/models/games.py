from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):
    title = models.CharField(max_length=200, verbose_name="Game Title")
    genre = models.CharField(max_length=100, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    release_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title", "release_date"]