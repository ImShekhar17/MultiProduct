from django.core.management.base import BaseCommand
from userauth.models import Role

class Command(BaseCommand):
    help = "Create default roles (admin, manager, customer)"

    def handle(self, *args, **kwargs):
        roles = ["admin", "manager", "customer"]

        for role_name in roles:
            role, created = Role.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created role: {role_name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Role already exists: {role_name}"))

        self.stdout.write(self.style.SUCCESS("Default roles ensured successfully."))
