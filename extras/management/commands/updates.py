from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from operators.models import QuoteRequest, TourOperator, Itinerary, ItineraryType
from users.models import UserProfile
import MySQLdb
from django.db.models import Count
from django.contrib.auth.models import User
from places.models import Park, CountryIndex
from photos.models import Photo
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
            tour_operator.update_photos_count()
            tour_operator.update_yas_score()
            for country in tour_operator.country_indexes.all():
                tour_operator.update_yas_score(country)

        print('Updated', tour_operators.count(), 'tour_operators')
        #activity_level
        itineraries = Itinerary.objects.filter(date_deleted=None) 
        for itinerary in itineraries:
            itinerary.activity_level = itinerary.calc_max_activity_level()
            itinerary.activity_level_name = itinerary.calc_activity_level_string()
            itinerary.save()
        print('Updated', itineraries.count(), 'itineraries')
        
        # update country
        countries = CountryIndex.objects.all()
        for country in countries:
            country.update_packages_count()
            country.update_photos_count()
            country.update_parks_count()
            country.update_operators_count()
        print('Updated', countries.count(), 'countries')

        # update articles
        articles = Article.objects.all()
        for article in articles:
            article.update_kudu_count()
            article.update_visit_count()
            article.update_comments_count()
        print('Updated', articles.count(), 'articles')

        # update tour operators
        tour_operators = TourOperator.objects.all()
        for tour_operator in tour_operators:
            tour_operator.update_reviews_count()
            tour_operator.update_average_rating()
            tour_operator.update_parks_count()
            tour_operator.update_packages_count()
            tour_operator.update_quote_request_count()
            tour_operator.update_photos_count()
            tour_operator.update_yas_score()
            for country in tour_operator.country_indexes.all():
                tour_operator.update_yas_score(country)
        print('Updated', tour_operators.count(), 'tour_operators')

        #parks
        parks = Park.objects.all()
        for park in parks:
            park.update_reviews_count()
            park.update_tour_operators_count()
            park.update_average_rating()
            park.update_packages_count()
            park.update_photos_count()
        print('Updated', parks.count(), 'parks')

        # update park reviews
        reviews = ParkReview.objects.all()
        for review in reviews:
            review.update_views_count()
            review.update_kudu_count()
        print('Updated', reviews.count(), 'park reviews')

        # update tour operator reviews
        reviews = TourOperatorReview.objects.all()
        for review in reviews:
            review.update_views_count()
            review.update_kudu_count()
        print('Updated', reviews.count(), 'tour op reviews')

        # update kilimanjaro reviews
        reviews = KilimanjaroParkReview.objects.all()
        for review in reviews:
            review.update_views_count()
            review.update_kudu_count()
        print('Updated', reviews.count(), 'kilimanjaro park reviews visit counts')

        objs = Itinerary.objects.all()
        for obj in objs:
            obj.update_visit_count()
        print('Updated', objs.count(), 'itinerary views')

        objs = UserProfile.objects.all()
        for obj in objs:
            obj.update_review_count()
            obj.update_kudus_count()
        print('Updated', objs.count(), 'users reviews and kudus')

        objs = Photo.objects.all()
        for obj in objs:
            obj.update_kudu_count()
        print('Updated', objs.count(), 'photos')

        self.stdout.write(self.style.SUCCESS("DONE"))
