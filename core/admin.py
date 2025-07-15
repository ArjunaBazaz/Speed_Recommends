from django.contrib import admin
from core.models import Game, Review, Likes, RecommendSiteUser

# Register your models here.
admin.site.register(Game)
admin.site.register(Review)
admin.site.register(Likes)
admin.site.register(RecommendSiteUser)