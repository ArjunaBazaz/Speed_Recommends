#core/models/admin.py
from django.contrib import admin
from core.models import Game, Review, Likes, RecommendSiteUser, SavedGame

# Register your models here.
admin.site.register(Game)
admin.site.register(Review)
admin.site.register(Likes)
admin.site.register(RecommendSiteUser)
admin.site.register(SavedGame)