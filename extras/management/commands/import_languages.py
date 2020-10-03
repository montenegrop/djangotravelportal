from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from places.models import Language
from django.core.files import File
import MySQLdb


class Command(BaseCommand):
    help = 'Import plugs'

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
        total = 0

        cursor.execute("select * from language")
        result = cursor.fetchall()
        for c in result:
            # create currency
            main = False
            if c['main'] == '1':
                main = True
            obj, is_created = Language.objects.get_or_create(
                name=c['name'], main=main
            )
            if is_created:
                total += 1
        message = 'Imported %i languages' % total

        self.stdout.write(self.style.SUCCESS(message))
