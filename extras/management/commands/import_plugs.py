from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from places.models import Plug
from django.core.files import File
import MySQLdb


class Command(BaseCommand):
    help = 'Import plugs'

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
        total = 0

        cursor.execute("select * from plug")
        result = cursor.fetchall()
        for c in result:
            # create currency
            obj, is_created = Plug.objects.get_or_create(
                name=c['plug_name']
            )
            if is_created:
                total += 1
            else:
                obj.image.delete(save=True)
            image_path = '%s/root/images/plugs/%s' % (
                options['base_location'], c['image_filename'],)
            image_file = open(image_path, "rb")
            obj.image.save("image_%s" %
                            obj.pk, File(image_file), save=True)
            obj.save()
        message = 'Imported %i plugs' % total

        self.stdout.write(self.style.SUCCESS(message))
