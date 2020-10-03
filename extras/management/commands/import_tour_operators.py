from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from lodges.models import *
from django.db import connections
from places.models import Country, Currency, Continent
from operators.models import TourOperator
from django.utils.timezone import make_aware
import MySQLdb
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = 'Import Tour Operator'

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
        cursor.execute("""
        select * from touroperator 
        join country on country.id = touroperator.headquarters
        join package on package.id = touroperator.package_id
        where date_deleted is null
        """)
        result = cursor.fetchall()
        for c in result:
            date_deleted = c['date_deleted']
            if date_deleted:
                date_deleted = make_aware(date_deleted)
            date_created = c['date_created']
            if date_created:
                date_created = make_aware(date_created)
            date_modified = c['date_modified']
            if date_modified:
                date_modified = make_aware(date_modified)
            last_seen = c['last_seen']
            if last_seen:
                last_seen = make_aware(last_seen)
            last_reviewed = c['last_reviewed']
            if last_reviewed:
                last_reviewed = make_aware(last_reviewed)
            startup_date = c['startup_date']
            package, _ = Package.objects.get_or_create(name=c['package.name'])
            obj, is_created = TourOperator.objects.update_or_create(
                slug=c.pop('name_slugged'),
                defaults={
                    'name': c['name'],
                    'headquarters': Country.objects.get(name=c['country']),
                    'package': package,
                    'website': c['website'],
                    'description': c['description'],
                    'vehicle_description': c['vehicle_description'],
                    'awards': c['awards'],
                    'projects': c['projects'],
                    'contact': c['contact'],
                    'email': c['email'],
                    'secondary_email': c['secondary_email'],
                    'telephone': c['telephone'],
                    'youtube': c['youtube'],
                    'linkedin': c['linkedin'],
                    'twitter': c['twitter'],
                    'pinterest': c['pinterest'],
                    'yas_modifier': c['yas_modifier'],
                    'facebook': c['facebook'],
                    'date_deleted': date_deleted,
                    'date_created': date_created,
                    'date_modified': date_modified,
                    'last_seen': last_seen,
                    'last_reviewed': last_reviewed,
                    'tailored_safari': c['tailored_safari'] if c['tailored_safari'] else 0,
                    'book_attraction': c['book_attraction'] if c['book_attraction'] else 0,
                    'international_flight': c['international_flight'] if c['international_flight'] else 0,
                    'group_safari': c['group_safari'] if c['group_safari'] else 0,
                    'validated': c['validated'],
                    'first_kudu_email': c['first_kudu_email'],
                    'not_trading': c['not_trading'] if c['not_trading'] else 0,
                    'out_of_business': c['out_of_business'] if 'out_of_business' in c and c['out_of_business'] != None else 0,
                    'suppress_email': c['suppress_email'] if c['suppress_email'] else 0,
                    'is_active': c['is_active'],
                    'blog': c['blog'],
                    'startup_date': startup_date
                })
            if is_created:
                created += 1
            else:
                obj.logo.delete(save=True)
                updated += 1
            if c['logo_path']:
                image_path = '%sroot/%s' % (
                    options['base_location'], c['logo_path'],)
                image_file = open(image_path, "rb")
                obj.logo.save("image_%s" % obj.pk, File(image_file), save=True)
            if c['luxury_level'] == 'High-end':
                obj.luxury_level = TourOperator.LUXURY_LEVEL_MID_LEVEL
            if c['luxury_level'] == 'Mid-level':
                obj.luxury_level = TourOperator.LUXURY_LEVEL_BUDGET
            if c['luxury_level'] == 'Luxury':
                obj.luxury_level = TourOperator.LUXURY_LEVEL_ULTRA_SAFARI
            obj.save()

            # add languages
            SQL = """
            select touroperator.name, language.name 
            FROM
            touroperator_language, language, touroperator 
            WHERE
            touroperator_language.language_id = language.id AND
            touroperator_language.touroperator_id = touroperator.id AND
            touroperator.id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                language = Language.objects.get(name=c_['name'])
                obj.languages.add(language)

            # touroperator_countryindex
            SQL = """
            select countryindex.country_name
            FROM
            touroperator_countryindex, countryindex
            WHERE
            touroperator_countryindex.countryindex_id = countryindex.id AND
            touroperator_countryindex.touroperator_id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                country_index = CountryIndex.objects.get(
                    name=c_['country_name'])
                obj.country_indexes.add(country_index)
            obj.save()

            # touroperator_parks
            SQL = """
            select park.park_name
            FROM
            touroperator_park, park
            WHERE
            touroperator_park.park_id = park.id AND
            touroperator_park.touroperator_id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                park = Park.objects.get(name=c_['park_name'])
                obj.parks.add(park)
            obj.save()

            # touroperatorpermission
            SQL = """
            SELECT
                touroperator_id, user.email_address
            FROM
                touroperatorpermission, user
            WHERE
            touroperatorpermission.user_id = user.id AND
            touroperatorpermission.touroperator_id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                if c_['email_address'] == 'undefined':
                    continue
                try:
                    user = User.objects.get(email=c_['email_address'])
                    if user:
                        user.profile.tour_operator = obj
                        to_group, _ = Group.objects.get_or_create(name='Tour Operator')
                        user.groups.add(to_group)
                        user.profile.save()
                except ObjectDoesNotExist:
                    print('User ' + str(c_['email_address']) + 'doesnotexists')
                    continue
                #print('Updated ' + str(c_['email_address']) + ' with tour operator ' + obj.name)
        message = 'Imported %i updated %i tour operators' % (created, updated)
        self.stdout.write(self.style.SUCCESS(message))
