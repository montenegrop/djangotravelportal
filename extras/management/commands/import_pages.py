from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from core.models import Page
from django.core.files import File
import MySQLdb
import os.path


class Command(BaseCommand):
    help = 'Import pages'

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
        cursor.execute("""
        SELECT * 
        FROM page
        """)
        result = cursor.fetchall()
        for c in result:
            newdict = {}
            newdict['title'] = c['title']
            newdict['slug'] = c.pop('web_path')
            newdict['content'] = c.pop('html')
            newdict['content'] = newdict['content'].replace("[% date.format(date.now, &#39;%Y&#39;, &#39;en_GB&#39;) -%]",'{{current_year}}')
            newdict['meta_title'] = c.pop('title')
            newdict['meta_keywords'] = c.pop('meta_keywords')
            newdict['meta_description'] = c.pop('meta_description')
            obj, is_created = Page.objects.update_or_create(
                slug=newdict.pop('slug'),defaults=newdict
            )
            if is_created:
                created += 1
            else:
                obj.image.delete(save=True)
                updated += 1
            
            if c['header_image_path']:
                image_path = '%sroot/%s' % (options['base_location'], c['header_image_path'],)                
                if os.path.exists(image_path):
                    image_file = open(image_path, "rb")
                    obj.image.save("image_%s" %
                                   obj.pk, File(image_file), save=True)
            

            obj.save()
        message = 'Imported %i updated %i pages' % (created, updated)
        self.stdout.write(self.style.SUCCESS(message))
