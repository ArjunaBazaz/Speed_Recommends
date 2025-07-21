from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from core.models.reviews import Review
from core.models.games import Game
from django.utils import timezone

@login_required
def add_review_1(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    score = request.POST.get('score')
    text = request.POST.get('review_text', '')

    if score is None:
        # Optionally handle missing score
        return redirect('review_form', game_id=game.id)

    review, created = Review.objects.get_or_create(
        user=request.user, game=game,
        defaults={'score': score, 'text': text, 'reviewTime': timezone.now()}
    )

    if not created:
        review.scores = score
        review.review_text = text
        review.reviewTime = timezone.now()
        review.save()

    return redirect('core:game_detail', game_id=game.id)