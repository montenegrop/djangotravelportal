from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from core.models import *

class Command(BaseCommand):
    help = 'Import social networks'

    def handle(self, *args, **options):
        #not allowed in production
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
        names = ['Instagram', 'Flickr', 'Twitter', 'Facebook', 'Pinterest', 'Youtube', 'LinkedIn', 'Trip Advisor', 'Blog']
        total = 0
        for snm in names:
            obj, is_created = SocialNetwork.objects.get_or_create(name=snm)
            if is_created:
                total += 1
        message = 'Imported %i social networks' % total
        self.stdout.write(self.style.SUCCESS(message))