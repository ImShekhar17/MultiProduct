from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Creates a superuser if none exist'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username=os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin'),
                email=os.getenv('DJANGO_SUPERUSER_EMAIL', 'naurangilal9675329115@gmail.com'),
                password=os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin@123')
            )
            self.stdout.write(self.style.SUCCESS('Superuser created'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists'))
