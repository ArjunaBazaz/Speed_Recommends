from django.conf import settings
from django.db import models

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name


class Platform(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name


class Developer(models.Model):    
    name = models.CharField(max_length=100, unique=True, db_index=True)

    def __str__(self):
        return self.name