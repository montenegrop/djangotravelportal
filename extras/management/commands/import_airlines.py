from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from places.models import Airline, Country, Park, CountryIndex
from django.core.files import File
import MySQLdb


class Command(BaseCommand):
    help = 'Import airlines'

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

        cursor.execute("select * from airline order by name")
        result = cursor.fetchall()
        for c in result:
            newdict = {}
            newdict['name'] = c.pop('name')
            newdict['website'] = c.pop('website')
            newdict['description'] = c.pop('description')

            cursor.execute("select * from country where id = ?")
            cursor.execute(SQL % c.pop('headquarters'))
            result = cursor.fetchall()
            for c__ in result:    
                newdict['headquarters'], _ = Country.objects.get(name=c__['country'])


            obj, is_created = Airline.objects.update_or_create(
                name=newdict.pop('name'), defaults=newdict
            )
            if is_created:
                created += 1
            else:
                obj.image.delete(save=True)
                updated += 1
            if c['image_path']:
                image_path = '%sroot%s' % (
                    options['base_location'], c['image_path'],)
                image_file = open(image_path, "rb")
                obj.image.save("image_%s" %
                               obj.pk, File(image_file), save=True)

            # countryIndexes
            SQL = """
            select countryindex.country_name, countryindex.country_name 
            FROM
            airline_countryindex, airline, countryindex 
            WHERE
            airline_countryindex.countryindex_id = countryindex.id AND
            airline_countryindex.airline_id = airline.id AND
            airline.id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                country_index = CountryIndex.objects.get(
                    name=c_['country_name'])
                obj.country_indexes.add(country_index)
            # parks

            SQL = """
            select park.park_name 
            FROM
            airline_park, airline, park
            WHERE
            airline_park.park_id = park.id AND
            airline_park.airline_id = airline.id AND
            airline.id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                park = Park.objects.get(name=c_['park_name'])
                obj.parks.add(park)

            obj.save()
        message = 'Imported %i updated %i airlines' % (created, updated)

        self.stdout.write(self.style.SUCCESS(message))
