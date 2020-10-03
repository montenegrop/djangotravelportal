from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from places.models import Animal, AnimalClass, CountryIndex, Park
from django.core.files import File
import MySQLdb


class Command(BaseCommand):
    help = 'Import animals'

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

        cursor.execute("select * from animal")
        result = cursor.fetchall()
        for c in result:
            newdict = {}
            newdict['name'] = c.pop('animal_name')
            newdict['name_short'] = c.pop('animal_name_short')
            newdict['slug'] = c.pop('animal_name_slugged')
            newdict['sub_heading'] = c.pop('animal_sub_heading')
            newdict['description'] = c.pop('animal_description')
            newdict['highlights'] = c.pop('animal_highlights')
            newdict['header_caption'] = c.pop('animal_header_caption')
            newdict['header_link'] = c.pop('animal_header_link')
            newdict['priority'] = c.pop('priority')
            newdict['meta_title'] = c.pop('meta_title')
            newdict['meta_keywords'] = c.pop('meta_keywords')
            newdict['meta_description'] = c.pop('meta_description')

            newdict['animal_class'], animal_class_is_created = AnimalClass.objects.get_or_create(
                name=c.pop('animal_class')
            )
            obj, is_created = Animal.objects.update_or_create(
                slug=newdict['slug'], defaults=newdict
            )
            if is_created:
                created += 1
            else:
                obj.image.delete(save=True)
                obj.image_mini.delete(save=True)
                obj.image_header.delete(save=True)
                updated += 1
            if c['animal_v2_image_path']:
                image_path = '%sroot/%s' % (
                    options['base_location'], c['animal_v2_image_path'],)
                image_file = open(image_path, "rb")
                obj.image.save("image_%s" %
                               obj.pk, File(image_file), save=True)

            if c['animal_mini_path']:
                image_path = '%sroot/%s' % (
                    options['base_location'], c['animal_mini_path'],)
                image_file = open(image_path, "rb")
                obj.image_mini.save("image_%s" %
                                    obj.pk, File(image_file), save=True)

            if c['animal_header_path']:
                image_path = '%sroot/%s' % (
                    options['base_location'], c['animal_header_path'],)
                image_file = open(image_path, "rb")
                obj.image_header.save("image_%s" %
                                      obj.pk, File(image_file), save=True)

            # add country index
            SQL = """
            select countryindex.country_name, animal.animal_name 
            FROM
            countryindex_animal, animal, countryindex 
            WHERE
            countryindex_animal.animal_id = animal.id AND
            countryindex_animal.countryindex_id = countryindex.id AND
            animal.id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                country_index, is_created = CountryIndex.objects.get_or_create(name=c_[
                                                                               'country_name'])
                obj.country_indexes.add(country_index)
            

            # parks
            SQL = """
            select park.park_name, animal.animal_name 
            FROM
            park_animal, animal, park 
            WHERE
            park_animal.animal_id = animal.id AND
            park_animal.park_id = park.id AND
            animal.id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                park, is_created = Park.objects.get_or_create(name=c_['park_name'])
                obj.parks.add(park)


            obj.save()
        message = 'Imported %i updated %i animals' % (created, updated)

        self.stdout.write(self.style.SUCCESS(message))
