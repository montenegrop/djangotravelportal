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
import os
import random 

class Command(BaseCommand):
    help = 'Analyze itineraries'


    def add_arguments(self, parser):
        parser.add_argument('-pics', required=True, type=str)

    def match_place(self, itinerary, pic):
        for park in itinerary.parks.all():
            if (park.name_short in pic or park.name in pic):
                return True
        for country_index in itinerary.country_indexes.all():
            if (country_index.name_short in pic or country_index.name in pic):
                return True
        return False

    def primary_match(self, itinerary, pic):
        if not itinerary.safari_focus_activity:
            return False
        return itinerary.safari_focus_activity.name in pic or itinerary.safari_focus_activity.name_short in pic

    def secondary_match(self, itinerary, pic):
        for act in itinerary.secondary_focus_activity.all():
            if act.name in pic or act.name_short in pic:
                return True
        return False

    def assign_itinerary_pic(self, itinerary, pics):
        random.seed(42)
        random.shuffle(pics)

        for pic in pics:
            if self.match_place(itinerary, pic) and self.primary_match(itinerary, pic):
                return pic
        for pic in pics:
            if self.match_place(itinerary, pic):
                return pic
        for pic in pics:
            if self.primary_match(itinerary, pic):
                return pic
        for pic in pics:
            if self.secondary_match(itinerary, pic):
                return pic
        return 'NO IMAGE FOUND'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
            return
        from operators.models import Itinerary, ItineraryDayDescription
        from places.models import Park
        itineraries = Itinerary.objects.filter(date_deleted__isnull=True)        
        itineraries = itineraries.filter(image='')
        pics = []
        pics_dir = options['pics']
        for root, dirs, files in os.walk(pics_dir):
            for file in files:
                pics.append(os.path.join(root, file))
        for i in itineraries:
            #give the itinerary a suitable image
            result_pic = self.assign_itinerary_pic(i, pics)
            parks = ' '.join([x.name_short for x in i.parks.all()])
            print("\"{}\",{},{},{},{}".format(i,i.tour_operator.name, i.safari_focus_activity, parks, result_pic))
        self.stdout.write(self.style.SUCCESS("DONE"))
