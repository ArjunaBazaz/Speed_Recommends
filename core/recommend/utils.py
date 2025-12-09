from sklearn.metrics.pairwise import cosine_similarity
from django.core.cache import cache
import pickle
import pandas as pd
#from surprise import Dataset, Reader, SVD
from core.models import Game, Likes, Review, SavedGame
import numpy as np
from django.db import models
import random

THRESHOLD = 10  #minimum reviews needed for collaborative

TFIDF_PATH = "tfidf_cache.pkl"

GLOBAL_MIN_YEAR = 1980
GLOBAL_MAX_YEAR = 2024

with open(TFIDF_PATH, "rb") as f:
    VECTORIZER, TFIDF_MATRIX, TFIDF_GAME_IDS = pickle.load(f)

ID_TO_IDX = {gid: i for i, gid in enumerate(TFIDF_GAME_IDS)}

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

def recommend_content_based(user, top_n=20, candidate_k=150):
    interaction_count = (
        Likes.objects.filter(user=user).count()
        + SavedGame.objects.filter(user=user).count()
    )

    cache_key = f"recs_{user.id}_{interaction_count}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    matrix = TFIDF_MATRIX
    game_ids = TFIDF_GAME_IDS

    id_to_idx = ID_TO_IDX

    # ✅ Likes → profile
    user_likes = Likes.objects.filter(user=user, vote=Likes.LIKE)
    liked_game_ids = [l.game_id for l in user_likes if l.game_id in id_to_idx]
    liked_idxs = [id_to_idx[gid] for gid in liked_game_ids]

    # ✅ Exclusions
    saved_ids = set(
        SavedGame.objects.filter(user=user)
        .values_list("game_id", flat=True)
    )
    voted_ids = set(
        Likes.objects.filter(user=user)
        .values_list("game_id", flat=True)
    )
    exclude_ids = saved_ids | voted_ids

    # ✅ FAST COLD START (NO order_by("?"))
    if not liked_idxs:
        candidate_ids = list(
            Game.objects.exclude(id__in=exclude_ids)
            .values_list("id", flat=True)
        )

        sampled_ids = random.sample(
            candidate_ids,
            min(top_n, len(candidate_ids))
        )

        pool = list(Game.objects.filter(id__in=sampled_ids))
        results = [(g, 0.0) for g in pool]
        cache.set(cache_key, results, timeout=300)
        return results

    # ✅ BUILD TF-IDF PROFILE (CACHED)
    profile_cache_key = f"profile_{user.id}_{interaction_count}"
    profile = cache.get(profile_cache_key)

    if profile is None:
        profile = np.asarray(matrix[liked_idxs].mean(axis=0))
        cache.set(profile_cache_key, profile, timeout=3600)

    # ✅ FAST PYTHON RANDOM SAMPLING (NO order_by("?"))
    eligible_ids = [gid for gid in game_ids if gid not in exclude_ids]

    candidate_ids = random.sample(
        eligible_ids,
        min(candidate_k, len(eligible_ids))
    )

    candidates = list(
        Game.objects
        .filter(id__in=candidate_ids)
        .prefetch_related("genres", "platforms", "developers")
    )

    # ✅ TF-IDF ONLY FOR CANDIDATES (NOT FULL MATRIX)
    candidate_idxs = [id_to_idx[g.id] for g in candidates if g.id in id_to_idx]
    candidate_vectors = matrix[candidate_idxs]

    candidate_sims = cosine_similarity(profile, candidate_vectors).flatten()

    # ✅ User attribute profile
    liked_games = list(
        Game.objects
        .filter(id__in=liked_game_ids)
        .prefetch_related("genres", "platforms", "developers")
    )

    user_genres = set(g.id for lg in liked_games for g in lg.genres.all())
    user_platforms = set(p.id for lg in liked_games for p in lg.platforms.all())
    user_devs = set(d.id for lg in liked_games for d in lg.developers.all())

    max_year = GLOBAL_MAX_YEAR
    min_year = GLOBAL_MIN_YEAR

    scored = []

    for i, g in enumerate(candidates):
        tfidf_score = candidate_sims[i]

        genre_overlap = len(user_genres & set(g.genres.values_list("id", flat=True)))
        platform_overlap = len(user_platforms & set(g.platforms.values_list("id", flat=True)))
        dev_overlap = len(user_devs & set(g.developers.values_list("id", flat=True)))

        attribute_score = (
            0.5 * genre_overlap
            + 0.3 * platform_overlap
            + 0.2 * dev_overlap
        )

        if g.release_year:
            year_norm = (g.release_year - min_year) / max(1, max_year - min_year)
        else:
            year_norm = 0.0

        recency_boost = 0.3 * year_norm
        baseline_boost = 0.2 * min(1.0, g.baseline_score / 10)

        final_score = (
            0.50 * tfidf_score
            + 0.30 * attribute_score
            + recency_boost
            + baseline_boost
        )

        scored.append((g, final_score))

    # ✅ Rank
    scored.sort(key=lambda x: -x[1])

    # ✅ DIVERSIFICATION
    diversified = []
    seen_titles = set()
    seen_devs = set()

    for g, score in scored:
        if len(diversified) >= top_n:
            break

        base_title = g.title.lower().split(":")[0]
        dev_ids = tuple(g.developers.values_list("id", flat=True))

        if base_title in seen_titles:
            continue
        if dev_ids and dev_ids[0] in seen_devs:
            continue

        seen_titles.add(base_title)
        seen_devs.add(dev_ids[0] if dev_ids else None)

        diversified.append((g, score))

    cache.set(cache_key, diversified, timeout=300)
    return diversified



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
