from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from places.models import Activity
from django.core.files import File
import MySQLdb
from ads.models import AdType, AdLocation, Ad, AdBanner
from operators.models import TourOperator, Itinerary
from photos.models import Photo
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import make_aware
from datetime import datetime
from places.models import Park, Activity
from operators.models import Itinerary
from photos.models import Photo

class Command(BaseCommand):
    help = 'Associate itineraries with random photo'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
            return
        itineraries = Itinerary.objects.filter(date_deleted__isnull=True)
        for i in itineraries:
                photos = i.photos.all()
                if photos.exists():
                    i.image = photo.first().image
                    i.save()
                    print('updated {}'.format(i.title))
                else:
                    print('no photos for {}'.format(i.title))
        self.stdout.write(self.style.SUCCESS("DONE"))
