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
from places.models import CountryIndex
import numpy as np

class Command(BaseCommand):
    help = 'Analyze itineraries'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
            return
        from operators.models import Itinerary, ItineraryDayDescription
        from places.models import Park
        itineraries = Itinerary.objects.filter(date_deleted__isnull=True)        
        itineraries = itineraries.filter(image='')
        for i in itineraries:
            parks = ' '.join([x.name_short for x in i.parks.all()])
            print("\"{}\",{},{},{}".format(i,i.tour_operator.name, i.safari_focus_activity, parks))
        self.stdout.write(self.style.SUCCESS("DONE"))
