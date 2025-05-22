from django.core.management.base import BaseCommand
from django.core.management import call_command
import os

class Command(BaseCommand):
    help = 'Loads admin user fixture into the database'

    def handle(self, *args, **options):
        self.stdout.write("Loading admin user fixture...")
        fixture_path = 'users/fixtures/admin_user.json'
        if not os.path.exists(fixture_path):
            self.stdout.write(self.style.ERROR(f"Fixture file {fixture_path} not found."))
            return
        try:
            with open(fixture_path, 'r', encoding='utf-8') as f:
                # Читаем файл, чтобы проверить кодировку
                content = f.read()
            call_command('loaddata', fixture_path, verbosity=1)
            self.stdout.write(self.style.SUCCESS("Admin user fixture loaded successfully."))
        except UnicodeDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Encoding error in fixture: {e}. Please re-create the fixture with UTF-8 encoding."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading fixture: {e}"))