from sklearn.metrics.pairwise import cosine_similarity
from django.core.cache import cache
import pickle
import pandas as pd
#from surprise import Dataset, Reader, SVD
from core.models import Game, Likes, Review, SavedGame
import numpy as np

THRESHOLD = 10  #minimum reviews needed for collaborative

TFIDF_PATH = "tfidf_cache.pkl"

def recommend_next(user):
    interaction_count = (Likes.objects.filter(user=user).count() + Review.objects.filter(user=user).count())
    #if interaction_count < THRESHOLD:
    if interaction_count < interaction_count+1:
        return recommend_content_based(user)
    # else:
    #     # hybrid or pure collaborative
    #     content_scores = recommend_content_based(user)
    #     collab_scores = recommend_collaborative(user)
    #     recommendations = blend_scores(content_scores, collab_scores)
    #     return recommendations

def recommend_content_based(user, top_n=20):
    interaction_count = Likes.objects.filter(user=user).count() + SavedGame.objects.filter(user=user).count()

    cache_key = f"recs_{user.id}_{interaction_count}"

    cached = cache.get(cache_key)
    if cached:
        return cached

    with open(TFIDF_PATH, "rb") as f:
        vectorizer, matrix, game_ids = pickle.load(f)

    id_to_idx = {gid: i for i, gid in enumerate(game_ids)}

    user_likes = Likes.objects.filter(user=user, vote=Likes.LIKE)
    liked_idxs = [id_to_idx[l.game_id] for l in user_likes if l.game_id in id_to_idx]

    saved_ids = set(
        SavedGame.objects
        .filter(user=user)
        .values_list("game_id", flat=True)
    )

    voted_ids = set(
        Likes.objects
        .filter(user=user)
        .values_list("game_id", flat=True)
    )

    exclude_ids = saved_ids | voted_ids

    if not liked_idxs:
        random_games = (
            Game.objects
            .exclude(id__in=exclude_ids)
            .order_by("?")[:top_n]
        )
        results = [(g, 0.0) for g in random_games]
        cache.set(cache_key, results, timeout=300)
        return results

    profile = np.asarray(matrix[liked_idxs].mean(axis=0))

    sims = cosine_similarity(profile, matrix).flatten()

    ranked = sorted(
        [
            (game_ids[i], sims[i])
            for i in range(len(game_ids))
            if game_ids[i] not in exclude_ids
        ],
        key=lambda x: -x[1]
    )

    top_game_ids = [gid for gid, _ in ranked[:top_n]]

    games = list(Game.objects.filter(id__in=top_game_ids))

    id_to_score = dict(ranked[:top_n])
    results = [(g, id_to_score.get(g.id, 0)) for g in games]

    cache.set(cache_key, results, timeout=300)

    return results

# def recommend_collaborative(user, top_n=10):
#     reviews = Review.objects.all().values_list('user_id', 'game_id', 'score')
#     reader = Reader(rating_scale=(1, 10))
#     data = Dataset.load_from_df(pd.DataFrame(reviews, columns=['user', 'item', 'rating']), reader)
#     trainset = data.build_full_trainset()
#     algo = SVD()
#     algo.fit(trainset)
#     # Score unseen games for user
#     liked_ids = Likes.objects.filter(user=user).values_list('game_id', flat=True)
#     reviewed_ids = Game.objects.filter(reviews__user=user).values_list('id', flat=True)
#     saved_game_ids = SavedGame.objects.filter(user=user).values_list('game_id', flat=True)

#     seen_ids = set(liked_ids).union(reviewed_ids).union(saved_game_ids)

#     unseen = Game.objects.exclude(id__in=seen_ids)

#     preds = [(g, algo.predict(user.id, g.id).est) for g in unseen]
#     return sorted(preds, key=lambda x: -x[1])[:top_n]

# def blend_scores(content, collab, w_content=0.3):
#     w_collab = 1 - w_content
#     collab_dict = {g.id: s for g, s in collab}

#     seen_game_ids = set()
#     blended = []

#     # Blend scores if present in both, or fallback
#     for g, score_c in content:
#         if g.id in seen_game_ids:
#             continue
#         score_f = collab_dict.get(g.id, 0)
#         blended_score = w_content * score_c + w_collab * score_f
#         blended.append((g, blended_score))
#         seen_game_ids.add(g.id)

#     # Add any remaining purely collaborative games not yet included
#     for g, score_f in collab:
#         if g.id in seen_game_ids:
#             continue
#         blended.append((g, w_collab * score_f))
#         seen_game_ids.add(g.id)

#     return sorted(blended, key=lambda x: -x[1])
