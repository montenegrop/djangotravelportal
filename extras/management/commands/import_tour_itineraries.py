from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from lodges.models import *
from django.db import connections
from places.models import Country, Currency, Continent, Activity, Animal
from operators.models import TourOperator, Itinerary, ItineraryType, Month
from django.utils.timezone import make_aware
import MySQLdb
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist
from ads.models import AdType, AdLocation, Ad, AdBanner
from analytics.models import Analytic
from operators.models import Itinerary, ItineraryExtra, ItineraryType
from blog.models import Article


class Command(BaseCommand):
    help = 'Import Tour Operator Itinary'

    def add_arguments(self, parser):
        parser.add_argument('-db_host', required=True, type=str)
        parser.add_argument('-db_name', required=True, type=str)
        parser.add_argument('-db_user', required=True, type=str)
        parser.add_argument('-db_pass', required=True, type=str)

    def handle(self, *args, **options):
        # not allowed in production
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
        db = MySQLdb.connect(
            host=options['db_host'], db=options['db_name'], user=options['db_user'], password=options['db_pass'])

        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        created, updated = 0, 0
        cursor.execute("""
        select 
        DISTINCT(touroperatoritinerary.itinerary_title_slugged),
        touroperatoritinerary.*, 
        touroperator.name as t_name 
        from 
        touroperatoritinerary join touroperator 
        on touroperatoritinerary.touroperator_id = touroperator.id
        """)
        dones = {}
        result = cursor.fetchall()
        for c in result:
            try:
                tour_operator_obj = TourOperator.objects.get(name=c['t_name'])
            except ObjectDoesNotExist:
                continue
            # create itineray_type_obj
            it_type_obj, dummy = ItineraryType.objects.update_or_create(
                name=c['itinerary_type']
            )
            c.pop('date_deleted')

            obj, is_created = Itinerary.objects.update_or_create(
                slug=c.pop('itinerary_title_slugged'),
                title=c['itinerary_title'],
                date_created=make_aware(c['date_created']),
                defaults={
                    'itinerary_type': it_type_obj,
                    'tour_operator': tour_operator_obj,
                    'content': c['itinerary_copy'],
                    'title': c['itinerary_title'],
                    'header': c['itinerary_header'],
                    'title_short': c['itinerary_title_short'],
                    'summary': c['itinerary_summary'],
                    'flight': c['itinerary_flight']
                    'accomodation': c['itinerary_accomodation'],
                    'currency': Currency.objects.get(code=c['itinerary_currency']),
                    'min_price': c['itinerary_min_price'],
                    'max_price': c['itinerary_max_price'],
                    'search_price': c['itinerary_search_price'],
                    'duration': c['itinerary_duration'],
                    'days': c['itinerary_days'],
                    'date_created': make_aware(c['date_created']),
                    'date_modified': make_aware(c['date_modified']),
                }
            )
            #TODO update duplicated slugs
            if is_created:
                created += 1
            else:
                updated += 1
            # add activity
            SQL = """
            select activity.activity_name
            FROM
            touroperatoritinerary_activity, activity
            WHERE
            touroperatoritinerary_activity.activity_id = activity.id AND
            touroperatoritinerary_id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            # obj.activities.all().clear()
            for c_ in result_:
                other = Activity.objects.get(name=c_['activity_name'])
                obj.activities.add(other)

            # add animals
            SQL = """
            select animal.animal_name
            FROM
            touroperatoritinerary_animal, animal
            WHERE
            touroperatoritinerary_animal.animal_id = animal.id AND
            touroperatoritinerary_id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            # obj.animals.all().clear()
            for c_ in result_:
                other = Animal.objects.get(name=c_['animal_name'])
                obj.animals.add(other)

            #photos
            SQL = """
            select photo.uuid
            FROM
            photo, album
            WHERE
            album.id = photo.album_id AND
            album_id = '%i'
             """
            cursor.execute(SQL % c['album_id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                photo = Photo.objects.get(uuid=c_['uuid'])
                photo.itinerary = obj
                photo.save()
                ###
                ### find the one that matches the aspect ratio
                itinerary.image = photo.image
                break
                ### 
                ###
            itinerary.save()
            # add countryindex
            SQL = """
            select countryindex.country_name
            FROM
            touroperatoritinerary_countryindex, countryindex
            WHERE
            touroperatoritinerary_countryindex.countryindex_id = countryindex.id AND
            touroperatoritinerary_id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            # obj.country_indexes.all().clear()
            for c_ in result_:
                other = CountryIndex.objects.get(name=c_['country_name'])
                obj.country_indexes.add(other)

            # add park
            SQL = """
            select park.park_name
            FROM
            touroperatoritinerary_park, park
            WHERE
            touroperatoritinerary_park.park_id = park.id AND
            touroperatoritinerary_id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            # obj.parks.all().clear()
            for c_ in result_:
                other = Park.objects.get(name=c_['park_name'])
                obj.parks.add(other)

            # add months
            SQL = """
            select month.name
            FROM
            touroperatoritinerary_month, month
            WHERE
            touroperatoritinerary_month.month_id = month.id AND
            touroperatoritinerary_id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            # obj.months.all().clear()
            for c_ in result_:
                other = Month.objects.get(name=c_['name'])
                obj.months.add(other)
            obj.save()
        message = 'Imported %i updated %i tour itinerary' % (created, updated)
        self.stdout.write(self.style.SUCCESS(message))
