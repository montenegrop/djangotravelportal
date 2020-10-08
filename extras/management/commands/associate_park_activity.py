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

def nan_equal(a,b):
    try:
        np.testing.assert_equal(a,b)
    except AssertionError:
        return False
    return True

class Command(BaseCommand):
    help = 'Associate parks with primary and secondary activity'

    def add_arguments(self, parser):
        parser.add_argument('-csv', required=True, type=str)

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
            return
        import pandas as pd
        from places.models import Park, Activity
        df = pd.read_csv(options['csv'])
        print(df.columns)
        for k,v in df.iterrows():
            if not v['name'] or nan_equal(v['name'], np.nan):
                continue
            print(v['name'])
            park = Park.objects.get(name=v['name'])
            park.safari_focus_activity = Activity.objects.get(name_short=v['1st'])
            print(v['secondary'],v['secondary.1'],v['secondary.2'],)
            if not nan_equal(v['secondary'], np.nan):
                print(v['secondary'])
                #park.secondary_focus_activity.add(Activity.objects.get(name_short=v['secondary']))
            if not nan_equal(v['secondary.1'], np.nan) :
                #park.secondary_focus_activity.add(Activity.objects.get(name_short=v['secondary.1']))
                pass
            if not nan_equal(v['secondary.2'], np.nan) :
                #park.secondary_focus_activity.add(Activity.objects.get(name_short=v['secondary.2']))
                pass
            #park.save()
            print(park, park.safari_focus_activity, park.secondary_focus_activity.count())
        
        self.stdout.write(self.style.SUCCESS("DONE"))
