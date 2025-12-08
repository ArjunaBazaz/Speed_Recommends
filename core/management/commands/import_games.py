import csv
from django.core.management.base import BaseCommand
from core.models.games import Game
from core.models.game_info import Genre, Platform, Developer


class Command(BaseCommand):
    help = "Load games from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs["csv_file"]

        with open(csv_file, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            x = 0

            for row in reader:
                title = row["title"].strip()

                game, created = Game.objects.get_or_create(
                    title=title,
                    defaults={
                        "description": row.get("description", ""),
                        "release_date": row.get("release_date") or None,
                        "release_year": row.get("release_year") or None,
                        "baseline_score": float(row.get("baseline_score", 0)),
                    },
                )

                #GENRES (ManyToMany)
                genre_names = [g.strip() for g in row["genres"].split(",")]
                for name in genre_names:
                    genre, _ = Genre.objects.get_or_create(name=name)
                    game.genres.add(genre)

                #PLATFORMS (ManyToMany)
                platform_names = [p.strip() for p in row["platforms"].split(",")]
                for name in platform_names:
                    platform, _ = Platform.objects.get_or_create(name=name)
                    game.platforms.add(platform)

                #DEVELOPERS (ManyToMany)
                dev_names = [d.strip() for d in row["developers"].split(",")]
                for name in dev_names:
                    dev, _ = Developer.objects.get_or_create(name=name)
                    game.developers.add(dev)

                game.save()

                x+=1
                if(x % 300 == 0):
                    self.stdout.write(f"Imported {x} games...")