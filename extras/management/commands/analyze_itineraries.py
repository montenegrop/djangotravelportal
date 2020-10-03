from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from places.models import Activity
from django.core.files import File
import MySQLdb
from ads.models import AdType, AdLocation, Ad, AdBanner
from operators.models import TourOperator, Itinerary
from photos.models import Photo
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import make_aware
from datetime import datetime
from places.models import CountryIndex
import numpy as np

def nan_equal(a,b):
    try:
        np.testing.assert_equal(a,b)
    except AssertionError:
        return False
    return True

class Command(BaseCommand):
    help = 'Analyze itineraries'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
            return
        import re
        from html.parser import HTMLParser
        pars = HTMLParser()
        from operators.models import Itinerary, ItineraryDayDescription
        from places.models import Park
        itineraries = Itinerary.objects.filter(date_deleted__isnull=True)        
        found = 0
        parks = Park.objects.all()
        all_count = 0
        for i in itineraries:
            content = re.sub(' +', ' ', i.content)
            regex = r"days?\s\d{1,2}"
            matches = re.finditer(regex, content, re.MULTILINE | re.IGNORECASE)
            results = []
            for matchNum, match in enumerate(matches, start=1):                
                #print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
                result = {}
                result['start'] = match.start()
                result['end'] = match.end()
                result['group'] = match.group()
                results.append(result)
            if len(results) > 0:
                all_count += 1
            else:
                continue
            dd = ItineraryDayDescription.objects.filter(itinerary=i)
            #for d in dd:
            dd.delete()
            print(i.pk, i.slug)
            for k,v in enumerate(results):
                number = re.findall(r'\d+', v['group'])[0]
                if k == len(results) - 1:
                    #last one
                    description = content[v['start']: ]
                    i.days = number
                else:
                    #not the last one, go to the next result
                    description = content[v['start']: results[k+1]['start']]
                selected_parks = []
                for park in parks:
                    if park.name in description or park.name_short in description:
                        selected_parks.append(park)
                
                day = ItineraryDayDescription()
                day.day_number = k
                day.itinerary = i
                day.title = 'Day {}'.format(number)
                day.lodging = ''
                #clean html tags
                TAG_RE = re.compile(r'<[^>]+>')
                description = TAG_RE.sub('', description[:5000])
                #special chars
                description =  pars.unescape(description)
                day.description = description

                day.save()
                day.parks.set(selected_parks)
            print('*' * 10)
            i.save()
        print(itineraries.count(), all_count)
        self.stdout.write(self.style.SUCCESS("DONE"))
