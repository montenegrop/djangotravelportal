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
    help = 'Import Packages'

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
        select * from package
        """)
        result = cursor.fetchall()
        for c in result:
            result = cursor.fetchall()
        for c in result:
            # create currency
            obj, is_created = Package.objects.get_or_create(
                name=c.pop('name'), defaults=c
            )
            if is_created:
                total += 1
            obj.save()
        message = 'Imported %i plugs' % total
