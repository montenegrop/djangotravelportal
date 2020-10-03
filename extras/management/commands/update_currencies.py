from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from places.models import Currency
import requests
from django.utils import timezone

class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        # update tour operators
        r = requests.get('http://openexchangerates.org/api/latest.json?app_id=22e345ca3920462dba25dfb55c2f9813')
        try:
            for key in r.json()['rates']:
                try:
                    currency = Currency.objects.get(code=key)
                except Currency.DoesNotExist:
                    continue
                currency.usd_exchange_rate = r.json()['rates'][key]
                currency.date_modified = timezone.now()
                currency.save()
            self.stdout.write(self.style.SUCCESS("DONE"))
        except KeyError:
                self.stdout.write(self.style.ERROR('Could not get any rates from openexchangerates.org'))


        
