from django.core.management.base import BaseCommand
from core.models.games import Game
import csv
import datetime
from decimal import Decimal

class Command(BaseCommand):
    help = 'Import games from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str)

    def handle(self, *args, **kwargs):
        csv_path = kwargs['csv_path']

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                if count >= 100:
                    break

                release_year = row.get('Release Year', '').strip()
                if release_year.isdigit():
                    release_date = datetime.date(int(release_year), 1, 1)
                else:
                    release_date = None

                # Convert price properly
                try:
                    price = Decimal(row['price'].strip())
                except Exception:
                    price = Decimal('0.00')  # or skip the row if invalid

                Game.objects.create(
                    title=row['Game Title'].strip(),
                    genre=row['Genre'].strip(),
                    price=price,
                    release_date=release_date,
                    platform=row['Platform'].strip()
                )
                count += 1

            self.stdout.write(self.style.SUCCESS(f'Imported {count} games'))
