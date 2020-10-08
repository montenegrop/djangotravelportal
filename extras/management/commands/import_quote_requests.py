from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from lodges.models import *
from django.db import connections
from places.models import Country, Currency, Continent
from operators.models import TourOperator
from django.utils.timezone import make_aware
import MySQLdb
from django.core.files import File
from operators.models import QuoteRequest, TourOperator, Itinerary, ItineraryType
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    help = 'Import Quote Requests'

    def add_arguments(self, parser):
        parser.add_argument('-db_host', required=True, type=str)
        parser.add_argument('-db_name', required=True, type=str)
        parser.add_argument('-db_user', required=True, type=str)
        parser.add_argument('-db_pass', required=True, type=str)
        parser.add_argument('-base_location', required=True, type=str)

    def handle(self, *args, **options):
        # not allowed in production
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
        db = MySQLdb.connect(
            host=options['db_host'], db=options['db_name'], user=options['db_user'], password=options['db_pass'])
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        created, updated = 0, 0
        QuoteRequest.objects.all().delete()
        cursor.execute("""
        select *,
        touroperator.name as tour_operator,
        user.email_address
        from touroperatorinformation 
        LEFT JOIN touroperator ON touroperatorinformation.touroperator_id = touroperator.id
        LEFT JOIN user ON user.id = touroperatorinformation.user_id
        """)
        result = cursor.fetchall()
        for c in result:
            obj = QuoteRequest()
            tour_operator_name = c['tour_operator']
            tour_operator_obj = False
            if tour_operator_name:
                try:
                    tour_operator_obj = TourOperator.objects.get(
                        name=tour_operator_name)
                except ObjectDoesNotExist:
                    #print('Tour ' + str(c['tour_operator']) + 'doesnotexists')
                    continue
            username = c.pop('email_address')
            try:                
                user = User.objects.get(email=username)
            except ObjectDoesNotExist:
                user = None
                print('User ' + str(username) + 'doesnotexists')
            obj.tour_operator = tour_operator_obj
            obj.date_trip = c.pop('trip_date')

            date_created = c.pop('date_created')
            if date_created:
                date_created = make_aware(date_created)
            obj.date_created = date_created

            date_modified = c.pop('date_modified')
            if date_modified:
                date_modified = make_aware(date_modified)
            obj.date_modified = date_modified

            date_deleted = c.pop('date_deleted')
            if date_deleted:
                date_deleted = make_aware(date_deleted)
            obj.date_deleted = date_deleted

            obj.user = user
            obj.name = c.pop('name')
            obj.email = c.pop('email')
            days = c.pop('days')
            if days == '30+':
                days = 30
            obj.days = days
            obj.telephone = c.pop('telephone')
            safary_type = c.pop('safari_type')
            if safary_type:
                itinerary_type, dummy = ItineraryType.objects.get_or_create(name=safary_type)
                if itinerary_type:
                    obj.itinerary_type = itinerary_type
            obj.party_size = c.pop('party_size')
            obj.regarding_text = c.pop('regarding_text')
            obj.additional_information = c.pop('additional_information')
            obj.follow_up_email_sent = c.pop('follow_up_email_sent')
            obj.ip_address = c.pop('ip_address')
            
            obj.save()

            # add country index
            SQL = """
            select countryindex.country_name as country_name
            FROM
            touroperatorinformation_countryindex, countryindex
            WHERE
            touroperatorinformation_countryindex.countryindex_id = countryindex.id AND
            touroperatorinformation_countryindex.touroperatorinformation_id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                country_index, is_created = CountryIndex.objects.get_or_create(name=c_[
                                                                               'country_name'])
                obj.country_indexes.add(country_index)

            created += 1

        message = 'Imported %i updated %i quote requests' % (created, updated)
        self.stdout.write(self.style.SUCCESS(message))
