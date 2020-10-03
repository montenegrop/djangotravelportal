from django.core.management.base import BaseCommand, CommandError
import MySQLdb
from places.models import Country, Currency, Continent
from django.conf import settings
from django.core.files import File
import os.path


class Command(BaseCommand):
    help = 'Import User'

    def add_arguments(self, parser):
        parser.add_argument('-db_host', required=True, type=str)
        parser.add_argument('-db_name', required=True, type=str)
        parser.add_argument('-db_user', required=True, type=str)
        parser.add_argument('-db_pass', required=True, type=str)
        parser.add_argument('-base_location', required=True, type=str)

    def handle(self, *args, **options):
        #not allowed in production
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
        db = MySQLdb.connect(
            host=options['db_host'], db=options['db_name'], 
            user=options['db_user'], password=options['db_pass'],
            charset='utf8', use_unicode=True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        total = 0

        cursor.execute("select * from country order by country")
        result = cursor.fetchall()
        for c in result:
            continent_obj = Continent.objects.get(name_short=c['continent'])

            del c['continent']

            c['name'] = c['country']
            c['name_short'] = c['countryshort']
            
            del c['country']
            del c['countryshort']

            c['continent'] = continent_obj

            obj, is_created = Country.objects.update_or_create(name=c['name'], defaults=c)
            if is_created:
                total += 1

            image_path = '%sroot/%s' % (
                options['base_location'], 'images/flags-iso/64/%s.png' % c['iso'].lower(),)
            if os.path.isfile(image_path):
                image_file = open(image_path, "rb")
                obj.flag.save("image_%s" % obj.pk, File(image_file), save=True)
            else:
                self.stdout.write(self.style.WARNING(
                    "Flag for %s does not exists" % obj.name))

            image_path = '%sroot/%s' % (options['base_location'],
                                        'images/flags-iso/flat/64/%s.png' % c['iso'].lower(),)
            if os.path.isfile(image_path):
                image_file = open(image_path, "rb")
                obj.flag_flat.save("image_%s" %
                                   obj.pk, File(image_file), save=True)
            else:
                self.stdout.write(self.style.WARNING(
                    "Flat Flag for %s does not exists" % obj.name))

        message = 'Imported %i countries' % total

        self.stdout.write(self.style.SUCCESS(message))
