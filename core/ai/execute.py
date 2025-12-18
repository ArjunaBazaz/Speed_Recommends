# core/ai/execute.py
from django.db.models import Q
from core.models.games import Game
from .spec import SearchSpec

def run_spec(spec: SearchSpec):
    qs = Game.objects.all().only("id", "title", "release_year", "baseline_score")

    # Text query across a few fields; expand if you want.
    if spec.query_text:
        qs = qs.filter(
            Q(title__icontains=spec.query_text) |
            Q(description__icontains=spec.query_text) |
            Q(genres__name__icontains=spec.query_text) |
            Q(platforms__name__icontains=spec.query_text) |
            Q(developers__name__icontains=spec.query_text)
        )

    if spec.genres_any:
        qs = qs.filter(genres__name__in=spec.genres_any)

    if spec.platforms_any:
        qs = qs.filter(platforms__name__in=spec.platforms_any)

    if spec.developers_any:
        qs = qs.filter(developers__name__in=spec.developers_any)

    if spec.min_release_year is not None:
        qs = qs.filter(release_year__gte=spec.min_release_year)

    if spec.max_release_year is not None:
        qs = qs.filter(release_year__lte=spec.max_release_year)

    if spec.min_baseline_score is not None:
        qs = qs.filter(baseline_score__gte=spec.min_baseline_score)

    qs = qs.distinct()

    # Sorting
    if spec.sort_by == "baseline_score":
        qs = qs.order_by("-baseline_score", "-release_year", "title")
    elif spec.sort_by == "release_year":
        qs = qs.order_by("-release_year", "-baseline_score", "title")
    else:
        # "relevance" fallback ordering
        qs = qs.order_by("-baseline_score", "-release_year", "title")

    return qs[: spec.limit]
