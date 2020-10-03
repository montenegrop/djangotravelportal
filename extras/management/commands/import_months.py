from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from operators.models import Month
from django.core.files import File
import MySQLdb


class Command(BaseCommand):
    help = 'Import months'

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
        cursor.execute("select * from month")
        result = cursor.fetchall()
        for row in result:
            obj, is_created = Month.objects.update_or_create(
                name=row.pop('name'),
                defaults=row
            )
            if is_created:
                total += 1
            obj.save()
        message = 'Imported %i months' % total
        self.stdout.write(self.style.SUCCESS(message))
