from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from surprise import Dataset, Reader, SVD
from core import Game, Likes, Review

THRESHOLD = 5  #minimum reviews needed for collaborative

def recommend_next(user):
    if user.interaction_count < THRESHOLD:
        return recommend_content_based(user)
    else:
        # hybrid or pure collaborative
        content_scores = recommend_content_based(user)
        collab_scores = recommend_collaborative(user)
        return blend_scores(content_scores, collab_scores)

def recommend_content_based(user, top_n=10):
    games = Game.objects.all()
    corpus = [f"{g.genre} {g.title} {g.platform}" for g in games]
    vec = TfidfVectorizer().fit_transform(corpus)
    # Build user profile vector from liked games
    liked_idxs = [i for i, g in enumerate(games) if g.user_vote(user) == Likes.LIKE]
    # Weighted average of liked game vectors
    profile = vec[liked_idxs].mean(axis=0)
    sims = cosine_similarity(profile, vec).flatten()
    return sorted(zip(games, sims), key=lambda x: -x[1])[:top_n]

def recommend_collaborative(user, top_n=10):
    reviews = Review.objects.all().values_list('user_id', 'game_id', 'scores')
    reader = Reader(rating_scale=(1, 10))
    data = Dataset.load_from_df(pd.DataFrame(reviews, columns=['user', 'item', 'rating']), reader)
    trainset = data.build_full_trainset()
    algo = SVD()
    algo.fit(trainset)
    # Score unseen games for user
    unseen = [g for g in Game.objects.exclude(review__user=user)]
    preds = [(g, algo.predict(user.id, g.id).est) for g in unseen]
    return sorted(preds, key=lambda x: -x[1])[:top_n]

def blend_scores(content, collab, w_content=0.3):
    w_collab = 1 - w_content
    collab_dict = {g.id: s for g, s in collab}
    blended = []
    for g, score_c in content:
        score_f = collab_dict.get(g.id, 0)
        blended.append((g, w_content * score_c + w_collab * score_f))
    return sorted(blended, key=lambda x: -x[1])
