from django.core.management.base import BaseCommand, CommandError
from polls.models import Question as Poll
from django.conf import settings
import _mysql
from lodges.models import *
from places.models import Park
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Import lodges from .csv'

    def add_arguments(self, parser):
        parser.add_argument('csv', type=str)
        pass

    def handle(self, *args, **options):
        #not allowed in production
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
        #connect to database
        df = pd.read_csv(csv, sep='\t')
        df.columns = map(str.lower, data.columns)
        for k,v in df.iterrows():
            lodge = Lodge.objects.get(name__iexact=v.name)
            if not lodge:
                lodge = Lodge()
            lodge.name = v.name
            lodge.website = v.URL
            lodge.email = v.email
            lodge.phone = v.phone
            lodge.latitude = v.longitude
            lodge.longitude = v.latitude
    
            description = v.description

            park = Park.objects.get(name__iexact=v.park)
            if not park:
                park = Park(name=v.park)
                park.save()
                print("Saved new park %s" % v.park)
            lodge.park = park

            country = CountryIndex.objects.get(name__iexact=v.country)
            if not country:
                country = CountryIndex(name=v.country)
                country.save()
                print("Saved new country index %s" % v.pcountryark)
            lodge.countryIndex = country
            
            lodge.save()
            total += 1

        message = 'Imported %i lodges"' % total
        self.stdout.write(self.style.SUCCESS(message))
