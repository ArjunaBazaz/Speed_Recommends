from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from core.models.reviews import Likes
from core.models.games import Game

@login_required
def toggle_preference(request, game_id, vote_type):
    game = get_object_or_404(Game, id=game_id)
    existing = Likes.objects.filter(user=request.user, game=game).first()
    vote_value = Likes.LIKE if vote_type == "like" else Likes.DISLIKE

    if existing:
        if existing.vote == vote_value:
            existing.delete()  # user clicked same again: remove
        else:
            existing.vote = vote_value
            existing.save()
    else:
        Likes.objects.create(user=request.user, game=game, vote=vote_value)

    return redirect(request.META.get('HTTP_REFERER', "home"))
