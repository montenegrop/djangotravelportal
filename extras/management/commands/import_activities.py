from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from places.models import Activity
from django.core.files import File
import MySQLdb


class Command(BaseCommand):
    help = 'Import activities'

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
        cursor.execute("select * from activity")
        result = cursor.fetchall()
        for c in result:
            newdict = {}
            newdict['name'] = c.pop('activity_name')
            newdict['name_short'] = c.pop('activity_name_short')
            newdict['slug'] = c.pop('activity_name_slugged')
            activity_type = c.pop('activity_type')
            if activity_type == 'Safari':
                activity_type = 'SAFARI'
            if activity_type == 'Non-safari':
                activity_type = 'NON_SAFARI'
            newdict['activity_type'] = activity_type
            newdict['description'] = c.pop('activity_description')
            newdict['priority'] = c.pop('priority')
            newdict['meta_title'] = c.pop('meta_title')
            newdict['meta_keywords'] = c.pop('meta_keywords')
            newdict['meta_description'] = c.pop('meta_description')
            obj, is_created = Activity.objects.update_or_create(
                name=newdict.pop('name'), defaults=newdict
            )
            if is_created:
                total += 1
            else:
                obj.image.delete(save=True)

            if c['activity_v2_image_path']:
                image_path = '%sroot/%s' % (
                    options['base_location'], c['activity_v2_image_path'],)
                image_file = open(image_path, "rb")
                obj.image.save("image_%s" %
                               obj.pk, File(image_file), save=True)

            obj.save()
            if is_created:
                total += 1
        message = 'Imported %i activities' % total

        self.stdout.write(self.style.SUCCESS(message))
