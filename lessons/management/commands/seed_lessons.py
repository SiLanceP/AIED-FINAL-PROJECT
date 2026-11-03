from django.core.management.base import BaseCommand

from lessons.models import Exercise, Level
from lessons.seed_data import seed


class Command(BaseCommand):
    help = "Create/update the 5 levels and their exercises from lessons/seed_data.py"

    def handle(self, *args, **options):
        seed(Level, Exercise)
        self.stdout.write(self.style.SUCCESS(f"Seeded {Level.objects.count()} levels."))
