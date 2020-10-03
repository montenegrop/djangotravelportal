from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from places.models import Currency
from django.core.files import File
import MySQLdb
from django.utils.timezone import make_aware


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

        cursor.execute("select * from currency")
        result = cursor.fetchall()
        for row in result:
            row['date_modified'] = make_aware(row.pop('date_modified'))
            row.pop("id")
            obj, is_created = Currency.objects.update_or_create(
                code=row.pop('currency_code'),
                symbol=row.pop('currency_symbol'),
                defaults=row
            )
            if is_created:
                total += 1
            obj.save()
        message = 'Imported %i currencies' % total


        self.stdout.write(self.style.SUCCESS(message))
