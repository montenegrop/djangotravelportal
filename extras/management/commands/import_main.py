from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from analytics.models import Analytic
import sys


#remember to import parks and activities from test site

class Command(BaseCommand):
    help = 'Import plugs'

    def add_arguments(self, parser):
        parser.add_argument('-db_host', default="localhost", required=True, type=str)
        parser.add_argument('-db_name', required=True, type=str)
        parser.add_argument('-db_user', required=True, type=str)
        parser.add_argument('-db_pass', required=True, type=str)
        parser.add_argument('-base_location', type=str,
                            default="/home/juan/Desktop/juan/dev/yas/yas_shared/")

    def handle(self, *args, **options):
        """
        call_command('import_continents')
        call_command('import_plugs', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'],
                     base_location=options['base_location'])
        call_command('import_languages', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'])
        call_command('import_pages', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'],
                     base_location=options['base_location'])
        call_command('import_vaccinations', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'])
        call_command('import_currencies', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'])
        call_command('import_countries', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'],
                     base_location=options['base_location'])
        #DO NOT import activities
        #call_command('import_activities', db_host=options['db_host'],
        #             db_name=options['db_name'],
        #             db_user=options['db_user'],
        #             db_pass=options['db_pass'],
        #             base_location=options['base_location'])
        """
        call_command('import_parks', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'],
                     base_location=options['base_location'])
        call_command('import_country_indexes', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'],
                     base_location=options['base_location'])
        call_command('import_animals', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'],
                     base_location=options['base_location'])
        call_command('import_airlines', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'],
                     base_location=options['base_location'])
        call_command('import_categories', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'])
        """
        call_command('import_users', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'],
                     base_location=options['base_location'])
        call_command('import_articles', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'],
                     base_location=options['base_location'])
        call_command('import_pages', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'],
                     base_location=options['base_location'])
        
        call_command('import_packages', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'])
        call_command('import_tour_operators', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'],
                     base_location=options['base_location'])
        call_command('import_months', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'])

        Analytic.objects.all().delete()
        call_command('import_photos', db_host=options['db_host'],
                db_name=options['db_name'],
                db_user=options['db_user'],
                db_pass=options['db_pass'],
                base_location=options['base_location'])

        call_command('import_tour_itineraries', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'])

        call_command('associate_itinieraries_activities')
        call_command('import_ads', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'],
                     base_location=options['base_location'])
        call_command('import_park_reviews', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'])
        
        call_command('import_tour_operator_reviews', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'])
        
        call_command('import_quote_requests', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'],
                     base_location=options['base_location'])
        
        call_command('import_email_logs', db_host=options['db_host'],
                     db_name=options['db_name'],
                db_user=options['db_user'],
                db_pass=options['db_pass'])
        
        call_command('import_analytics', db_host=options['db_host'],
                     db_name=options['db_name'],
                     db_user=options['db_user'],
                     db_pass=options['db_pass'])
        call_command('updates')
        #call_command('update_visit_count')
        """
        message = 'End'
        self.stdout.write(self.style.SUCCESS(message))
