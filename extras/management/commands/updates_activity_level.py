from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from operators.models import QuoteRequest, TourOperator, Itinerary, ItineraryType
from users.models import UserProfile
import MySQLdb
from django.db.models import Count
from django.contrib.auth.models import User
from places.models import Park, CountryIndex
from blog.models import Article
from reviews.models import ParkReview, KilimanjaroParkReview, TourOperatorReview
from analytics.models import Analytic


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        #activity_level
        itineraries = Itinerary.objects.filter(date_deleted=None) 
        for itinerary in itineraries:
            itinerary.activity_level = itinerary.calc_max_activity_level()
            itinerary.activity_level_name = itinerary.calc_activity_level_string()
            itinerary.save()
        print('Updated', itineraries.count(), 'itineraries')
        self.stdout.write(self.style.SUCCESS("DONE"))
