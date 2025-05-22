from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Loads admin user fixture into the database'

    def handle(self, *args, **options):
        self.stdout.write("Loading admin user fixture...")
        try:
            call_command('loaddata', 'users/fixtures/admin_user.json', verbosity=1)
            self.stdout.write(self.style.SUCCESS("Admin user fixture loaded successfully."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading fixture: {e}"))