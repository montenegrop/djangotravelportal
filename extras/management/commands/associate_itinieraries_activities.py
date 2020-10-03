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

class Command(BaseCommand):
    help = 'Associate itineraries with activities based on parks'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
            return
        itineraries = Itinerary.objects.filter(date_deleted__isnull=True)
        photography = Activity.objects.get(name_short='Photography')
        for i in itineraries:
            parks = []
            primaries = []
            secondaries = []
            for park in i.parks.all():
                if park.safari_focus_activity:
                    i.safari_focus_activity = park.safari_focus_activity
                    primaries.append(park.safari_focus_activity.name_short)
                # add parks secondary and count them
                for second in park.secondary_focus_activity.all():
                    i.secondary_focus_activity.add(second)
                    secondaries.append(second.name_short)
                if 'photograph' in i.title.lower():
                    i.secondary_focus_activity.add(photography)
                    secondaries.append('photography')
                parks.append(park.name)
            try:
                a = i.safari_focus_activity
            except Activity.DoesNotExist:
                i.safari_focus_activity = Activity.objects.get(name_short='Game drives')
            # if has more than 3 secondaries, print it
            count = i.secondary_focus_activity.count()
            #print('{} has {} activities'.format(i.title, count))
            if count > 3:
                act = ','.join([x.name_short for x in i.secondary_focus_activity.all()])
                print('---- {} has {} activities - {}'.format(i.title, count, act))
            i.save()
            #parks = set(parks)
            #primaries = set(primaries)
            #secondaries = set(secondaries)
            #print('{},{},{},{}'.format(i.title, '-'.join(parks), '-'.join(primaries), '-'.join(secondaries), ))
        
        self.stdout.write(self.style.SUCCESS("DONE"))
