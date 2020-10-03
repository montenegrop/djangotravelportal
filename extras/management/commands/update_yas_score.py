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
        # update tour operators
        tour_operators = TourOperator.objects.all()
        for tour_operator in tour_operators:
            tour_operator.update_reviews_count()
            tour_operator.update_average_rating()
            tour_operator.update_parks_count()
            tour_operator.update_packages_count()
            tour_operator.update_quote_request_count()
            tour_operator.update_yas_score()
            for country in tour_operator.country_indexes.all():
                tour_operator.update_yas_score(country)
        print('Updated', tour_operators.count(), 'tour_operators')

        self.stdout.write(self.style.SUCCESS("DONE"))
