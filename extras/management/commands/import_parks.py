from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from places.models import Park, Activity
from django.core.files import File
import MySQLdb


class Command(BaseCommand):
    help = 'Import parks'

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
            host=options['db_host'], db=options['db_name'],
            user=options['db_user'], password=options['db_pass'],
            charset='utf8', use_unicode=True)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        total = 0

        cursor.execute("select * from park")
        result = cursor.fetchall()
        for c in result:
            newdict = {}
            newdict['name_short'] = c.pop('park_name_short')
            newdict['slug'] = c.pop('park_name_slugged')
            newdict['description'] = c.pop('description')
            newdict['getting_there'] = c.pop('getting_there')
            newdict['highlights'] = c.pop('highlights')
            newdict['meta_title'] = c.pop('meta_title')
            newdict['meta_keywords'] = c.pop('meta_keywords')
            newdict['meta_description'] = c.pop('meta_description')
            newdict['safari_suitability'] = c.pop('safari_suitability')
            newdict['anti_malaria'] = c.pop('anti_malaria')
            newdict['total_area'] = c.pop('total_area')
            newdict['image_caption'] = c.pop('image_caption')
            newdict['year_established'] = c.pop('year_established') or None
            newdict['safari_suitability_text'] = c.pop('safari_suitability_text')
            newdict['header_caption_link'] = c.pop('large_image_link')
            
            newdict['longitude'] = float(c.pop('longtitude'))
            newdict['latitude'] = float(c.pop('latitude'))

            
            obj, is_created = Park.objects.update_or_create(
                name=c.pop('park_name'), defaults=newdict
            )
            if is_created:
                total += 1
            else:
                obj.image.delete(save=True)
                obj.image_mini.delete(save=True)
            if c['large_image_path']:
                image_path = '%sroot/%s' % (
                    options['base_location'], c['large_image_path'],)
                image_file = open(image_path, "rb")
                obj.image.save("image_%s" %
                               obj.pk, File(image_file), save=True)
            if c['park_mini_path']:
                image_path = '%sroot/%s' % (
                    options['base_location'], c['park_mini_path'],)
                image_file = open(image_path, "rb")
                obj.image_mini.save("image_%s" %
                               obj.pk, File(image_file), save=True)

            # add activities
            SQL = """
            select park.park_name_short, activity.activity_name 
            FROM
            park_activity, activity, park 
            WHERE
            park_activity.activity_id = activity.id AND
            park_activity.park_id = park.id AND
            park.id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                activity = Activity.objects.get(name_old=c_['activity_name'])
                obj.activities.add(activity)
                
            obj.save()
            if is_created:
                total += 1
        message = 'Imported %i parks' % total

        self.stdout.write(self.style.SUCCESS(message))
