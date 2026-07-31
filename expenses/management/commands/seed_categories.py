from django.core.management.base import BaseCommand
from django.conf import settings

from expenses.models import Category


class Command(BaseCommand):
    help = "Seed the database with ExpenseFlow's default expense categories."

    def handle(self, *args, **options):
        created_count = 0
        for name, icon in settings.DEFAULT_CATEGORIES:
            _, created = Category.objects.get_or_create(
                user=None, name=name, defaults={'icon': icon, 'is_default': True}
            )
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded categories. {created_count} new categories created."))
