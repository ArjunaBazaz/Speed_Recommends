from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from surprise import Dataset, Reader, SVD
from core.models import Game, Likes, Review, SavedGame
import numpy as np

THRESHOLD = 2  #minimum reviews needed for collaborative

def recommend_next(user):
    interaction_count = (Likes.objects.filter(user=user).count() + Review.objects.filter(user=user).count())
    if interaction_count < THRESHOLD:
        return recommend_content_based(user)
    else:
        # hybrid or pure collaborative
        content_scores = recommend_content_based(user)
        collab_scores = recommend_collaborative(user)
        recommendations = blend_scores(content_scores, collab_scores)
        return recommendations

def recommend_content_based(user, top_n=10):
    games = Game.objects.all()
    corpus = [f"{g.genre} {g.title} {g.platform}" for g in games]
    vec = TfidfVectorizer().fit_transform(corpus)

    liked_idxs = [i for i, g in enumerate(games) if g.user_vote(user) == Likes.LIKE]
    seen_ids = set(g.id for g in games if g.user_vote(user) is not None)

    if not liked_idxs:
        random_games = Game.objects.exclude(id__in=seen_ids).order_by("?")[:top_n]
        return [(g, 0) for g in random_games]

    profile = vec[liked_idxs].mean(axis=0)
    sims = cosine_similarity(np.asarray(profile), vec).flatten()

    # pair and remove already seen
    results = [
        (g, s) for g, s in zip(games, sims)
        if g.id not in seen_ids
    ]

    return sorted(results, key=lambda x: -x[1])[:top_n]

def recommend_collaborative(user, top_n=10):
    reviews = Review.objects.all().values_list('user_id', 'game_id', 'score')
    reader = Reader(rating_scale=(1, 10))
    data = Dataset.load_from_df(pd.DataFrame(reviews, columns=['user', 'item', 'rating']), reader)
    trainset = data.build_full_trainset()
    algo = SVD()
    algo.fit(trainset)
    # Score unseen games for user
    liked_ids = Likes.objects.filter(user=user).values_list('game_id', flat=True)
    reviewed_ids = Game.objects.filter(reviews__user=user).values_list('id', flat=True)
    saved_game_ids = SavedGame.objects.filter(user=user).values_list('game_id', flat=True)

    seen_ids = set(liked_ids).union(reviewed_ids).union(saved_game_ids)

    unseen = Game.objects.exclude(id__in=seen_ids)

    preds = [(g, algo.predict(user.id, g.id).est) for g in unseen]
    return sorted(preds, key=lambda x: -x[1])[:top_n]

def blend_scores(content, collab, w_content=0.3):
    w_collab = 1 - w_content
    collab_dict = {g.id: s for g, s in collab}

    seen_game_ids = set()
    blended = []

    # Blend scores if present in both, or fallback
    for g, score_c in content:
        if g.id in seen_game_ids:
            continue
        score_f = collab_dict.get(g.id, 0)
        blended_score = w_content * score_c + w_collab * score_f
        blended.append((g, blended_score))
        seen_game_ids.add(g.id)

    # Add any remaining purely collaborative games not yet included
    for g, score_f in collab:
        if g.id in seen_game_ids:
            continue
        blended.append((g, w_collab * score_f))
        seen_game_ids.add(g.id)

    return sorted(blended, key=lambda x: -x[1])
