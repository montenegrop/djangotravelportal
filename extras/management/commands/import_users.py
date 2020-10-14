from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from lodges.models import *
from django.db import connections, connection
from places.models import Animal, Activity, CountryIndex, Country
from users.models import UserProfile, Badge
from django.core.management import call_command
from django.contrib.auth.models import Group
import MySQLdb
from django.core.files import File
from django.utils.timezone import make_aware
import os.path
import base64
import hashlib
import binascii
from django.contrib.auth.models import User


def transform_perl_django(perl_password):
    hash_and_salt = base64.b64decode(perl_password[6:])
    salt = hash_and_salt[-20:]
    hash = hash_and_salt[:-20]
    salt = base64.b64encode(salt).decode('utf-8')
    pwd = 'sha1$' + salt + '$' + binascii.hexlify(hash).decode('utf-8')
    return pwd


class Command(BaseCommand):
    help = 'Import User'

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
        cursor.execute("select * from user")
        result = cursor.fetchall()
        for c in result:
            if not c['email_address']:
                self.stdout.write(self.style.WARNING(
                    "User with None email found skipping it"))
                continue
            if c['last_login']:
                c['last_login'] = make_aware(c['last_login'])

            #if c['screen_name']:
            #    username = c.pop('screen_name')
            #else:
            #    username = c['email_address']
            obj_user, is_created = User.objects.update_or_create(
                username=c['email_address'],
                defaults={
                    'first_name': c['first_name'],
                    'last_name': c['last_name'],
                    'email': c['email_address'],
                    'is_active': c['is_active'],
                    'last_login': c['last_login'],
                    'password': transform_perl_django(c['password'])
                }
            )

            # delete the unused field
            email_address = c.pop('email_address')
            del c['first_name']
            del c['is_active']
            del c['last_backend']
            del c['last_email_sent']
            del c['last_name']
            del c['password']
            del c['uuid']
            del c['validated']
            
            user_id = c.pop('id')
            c['date_created'] = make_aware(c.pop('date_created'))
            if c['blog']:
                c['blog'] = c['blog'][:1500]
            obj, is_created = UserProfile.objects.update_or_create(
                user=obj_user,
                defaults=c
            )
            #todo check!
            if c['date_deleted']:
                obj_user.active = False
            obj.first_kudu_email = c['first_kudu_email']
            obj.suppress_email = c['suppress_email']
            if is_created:
                created += 1
            else:
                updated += 1
                obj.avatar.delete(save=True)
            if c['avatar_image']:
                image_path = '%s/root%s' % (
                    options['base_location'], c['avatar_image'],)
                if os.path.exists(image_path):
                    image_file = open(image_path, "rb")
                    obj.avatar.save("image_%s" %
                                    obj.pk, File(image_file), save=True)
            obj.user_type = c['type']
            SQL = """
            SELECT country.country as name
            FROM country, user
            WHERE
            user.country_id = country.id AND
            user.id = %s
            """
            cursor.execute(SQL % user_id)
            result_ = cursor.fetchall()
            for c_ in result_:
                country, dummy = Country.objects.get_or_create(name=c_['name'])
                obj.country = country
            obj.save()
            SQL = """
            SELECT role.role as name
            FROM user_role, user, role
            WHERE
            user_role.user_id = user.id AND
            user.id = %s
            """
            cursor.execute(SQL % user_id)
            result_ = cursor.fetchall()
            for c_ in result_:
                group, dummy = Group.objects.get_or_create(name=c_['name'])
                obj.user.groups.add(group)

            # user_activity
            SQL = """
            select activity.activity_name
            FROM
            user_activity, activity
            WHERE
            user_activity.activity_id = activity.id AND
            user_activity.user_id = %i
             """
            cursor.execute(SQL % user_id)
            result_ = cursor.fetchall()
            for c_ in result_:
                activity = Activity.objects.get(name_old=c_['activity_name'])
                obj.activities_enjoy.add(activity)
            obj.save()

            # countryIndexes
            SQL = """
            select countryindex.country_name
            FROM
            user_countryindex, countryindex
            WHERE
            user_countryindex.countryindex_id = countryindex.id AND
            user_countryindex.user_id = %i
             """
            cursor.execute(SQL % user_id)
            result_ = cursor.fetchall()
            for c_ in result_:
                country_index = CountryIndex.objects.get(name=c_['country_name'])
                obj.countries_visited.add(country_index)
            obj.save()
            # parks
            SQL = """
            select park.park_name
            FROM
            user_park, park
            WHERE
            user_park.park_id = park.id AND
            user_park.user_id = %i
             """
            cursor.execute(SQL % user_id)
            result_ = cursor.fetchall()
            for c_ in result_:
                park = Park.objects.get(name=c_['park_name'])
                obj.parks_visited.add(park)
            obj.save()
            
            # animals
            SQL = """
            select animal.animal_name
            FROM
            user_animal, animal
            WHERE
            user_animal.animal_id = animal.id AND
            user_animal.user_id = %i
             """
            cursor.execute(SQL % user_id)
            result_ = cursor.fetchall()
            for c_ in result_:
                animal = Animal.objects.get(name=c_['animal_name'])
                obj.animals_seen.add(animal)
            obj.save()
        message = 'Imported %i updated %i users' % (created, updated)
        self.stdout.write(self.style.SUCCESS(message))
