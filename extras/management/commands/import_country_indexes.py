from django.core.management.base import BaseCommand, CommandError
import MySQLdb
from places.models import CountryIndex, Plug, Animal, Activity, Language, Park, Currency, Continent, Vaccination
from django.conf import settings
from django.core.files import File

class Command(BaseCommand):
    help = 'Import Country Index'

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
            host=options['db_host'], db=options['db_name'], user=options['db_user'], password=options['db_pass'])
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        created = 0
        updated = 0
        cursor.execute("select * from countryindex")
        result = cursor.fetchall()
        for c in result:
            newdict = {}
            newdict['name'] = c.pop('country_name')
            newdict['name_short'] = c.pop('country_name_short')
            newdict['slug'] = c.pop('country_name_slugged')
            newdict['description'] = c.pop('description')
            caption = c.pop('countryindex_header_caption')
            newdict['header_caption'] = caption
            newdict['header_alt'] = caption
            if caption == '' or caption == None:
                print(newdict['name'], 'needs alt text')
            newdict['header_caption_link'] = c.pop('countryindex_header_link')
            newdict['large_caption'] = c.pop('large_image_caption')
            #newdict['feature'] = c.pop('feature')
            newdict['one_line_summary'] = c.pop('one_line_summary')
            newdict['summary'] = c.pop('summary')
            newdict['getting_there'] = c.pop('getting_there')
            newdict['highlights'] = c.pop('highlights')
            newdict['airports'] = c.pop('airports')
            newdict['capital'] = c.pop('capital')
            newdict['population'] = c.pop('population')
            newdict['total_area'] = c.pop('total_area')
            newdict['currency_code'] = c.pop('currency_code')
            newdict['currency_name'] = c.pop('currency')
            newdict['longitude'] = float(c.pop('longtitude'))
            newdict['latitude'] = float(c.pop('latitude'))
            newdict['meta_title'] = c.pop('meta_title')
            newdict['meta_keywords'] = c.pop('meta_keywords')
            newdict['meta_description'] = c.pop('meta_description')

            obj, is_created = CountryIndex.objects.update_or_create(
                name=newdict['name'], defaults=newdict
            )
            if is_created:
                created += 1
            else:
                updated += 1
                obj.flag.delete(save=True)
                obj.flag_flat.delete(save=True)
                obj.image.delete(save=True)
                obj.image_large.delete(save=True)
                obj.image_header.delete(save=True)

            if c['flag_filename']:
                image_path = '%sroot/images/flags/64/%s' % (
                    options['base_location'], c['flag_filename'],)
                image_file = open(image_path, "rb")
                obj.flag.save("image_%s" % obj.pk, File(image_file), save=True)

                image_path = '%sroot/images/flags/flat/64/%s' % (
                    options['base_location'], c['flag_filename'],)
                image_file = open(image_path, "rb")
                obj.flag_flat.save("image_%s" %
                                   obj.pk, File(image_file), save=True)

            if c['countryindex_header_path']:
                image_path = '%sroot/%s' % (
                    options['base_location'], c['countryindex_header_path'],)
                image_file = open(image_path, "rb")
                obj.image_header.save("image_%s" %
                                      obj.pk, File(image_file), save=True)

            if c['countryindex_image_path']:
                image_path = '%sroot/%s' % (
                    options['base_location'], c['countryindex_image_path'],)
                image_file = open(image_path, "rb")
                obj.image.save("image_%s" %
                               obj.pk, File(image_file), save=True)

            if c['large_image_path']:
                image_path = '%sroot/%s' % (
                    options['base_location'], c['large_image_path'],)
                image_file = open(image_path, "rb")
                obj.image_large.save("image_%s" %
                                     obj.pk, File(image_file), save=True)

            # add activities
            SQL = """
            select countryindex.country_name, activity.activity_name
            FROM
            countryindex_activity, activity, countryindex 
            WHERE
            countryindex_activity.activity_id = activity.id AND
            countryindex_activity.countryindex_id = countryindex.id AND
            countryindex.id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                activity = Activity.objects.get(name_old=c_['activity_name'])
                obj.activities.add(activity)

            # add languages
            SQL = """
            select countryindex.country_name, language.name 
            FROM
            countryindex_language, language, countryindex 
            WHERE
            countryindex_language.language_id = language.id AND
            countryindex_language.countryindex_id = countryindex.id AND
            countryindex.id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                language = Language.objects.get(name=c_['name'])
                obj.languages.add(language)
            # add parks
            SQL = """
            select countryindex.country_name, park.park_name 
            FROM
            countryindex_park, park, countryindex 
            WHERE
            countryindex_park.park_id = park.id AND
            countryindex_park.countryindex_id = countryindex.id AND
            countryindex.id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                park = Park.objects.get(name=c_['park_name'])
                obj.parks.add(park)
            # add plugs
            SQL = """
            select countryindex.country_name, plug.plug_name 
            FROM
            countryindex_plug, plug, countryindex 
            WHERE
            countryindex_plug.plug_id = plug.id AND
            countryindex_plug.countryindex_id = countryindex.id AND
            countryindex.id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                plug = Plug.objects.get(name=c_['plug_name'])
                obj.plugs.add(plug)
            # add vaccination
            SQL = """
            select countryindex.country_name, vaccination.vaccination_name 
            FROM
            countryindex_vaccination, vaccination, countryindex 
            WHERE
            countryindex_vaccination.vaccination_id = vaccination.id AND
            countryindex_vaccination.countryindex_id = countryindex.id AND
            countryindex.id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                vaccination = Vaccination.objects.get(
                    name=c_['vaccination_name'])
                obj.vaccinations.add(vaccination)
            # save!
            obj.save()
        message = 'Imported %i updated %i country indexes' % (created, updated)

        self.stdout.write(self.style.SUCCESS(message))
