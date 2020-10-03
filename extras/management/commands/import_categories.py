from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from blog.models import Category
from django.core.files import File
import MySQLdb


class Command(BaseCommand):
    help = 'Import categories'

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
        created, updated = 0, 0

        cursor.execute("select * from articlecategory")
        result = cursor.fetchall()
        for c in result:
            # create currency
            newdict = {}
            newdict['slug'] = c.pop('name_slugged')
            newdict['homepage_text'] = c.pop('homepage_text')
            newdict['description'] = c.pop('description')
            if c.pop('hide_menu') == '1':
                newdict['hidden'] = True
            obj, is_created = Category.objects.update_or_create(
                name=c.pop('name'), defaults=newdict
            )
            if is_created:
                created += 1
            else:
                updated += 1
            obj.save()
        message = 'Imported %i updated %i categories' % (created, updated)

        self.stdout.write(self.style.SUCCESS(message))
