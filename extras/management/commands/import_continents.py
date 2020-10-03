from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from places.models import Continent
from django.db import models


class Command(BaseCommand):
    help = 'Import social networks'

    def handle(self, *args, **options):
        # not allowed in production
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
        names = [('Asia', 'AS'), ('Europe', 'EU'), ('Africa', 'AF'), ('Oceania', 'OC'),
                 ('North America', 'NA'), ('Antarctica', 'AN'), ('South America', 'SA')]
        total = 0
        for name, name_short in dict(names).items():
            obj, is_created = Continent.objects.update_or_create(
                name=name, name_short=name_short)
            if is_created:
                total += 1
        message = 'Imported %i continents' % total
        self.stdout.write(self.style.SUCCESS(message))
