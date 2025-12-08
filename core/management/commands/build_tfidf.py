import pickle
from django.core.management.base import BaseCommand
from sklearn.feature_extraction.text import TfidfVectorizer

from core.models import Game

TFIDF_PATH = "tfidf_cache.pkl"

class Command(BaseCommand):
    help = "Build TF-IDF matrix for all games"

    def handle(self, *args, **kwargs):
        games = list(
            Game.objects
            .prefetch_related("genres", "platforms", "developers")
        )

        corpus = []
        for g in games:
            genre_text = " ".join(x.name for x in g.genres.all())
            platform_text = " ".join(x.name for x in g.platforms.all())
            dev_text = " ".join(x.name for x in g.developers.all())
            corpus.append(f"{genre_text} {platform_text} {dev_text} {g.title}")

        vectorizer = TfidfVectorizer(max_features=5000)
        matrix = vectorizer.fit_transform(corpus)

        with open(TFIDF_PATH, "wb") as f:
            pickle.dump((vectorizer, matrix, [g.id for g in games]), f)

        self.stdout.write("✅ TF-IDF cache built")
