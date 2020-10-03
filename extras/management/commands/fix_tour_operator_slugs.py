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
from operators.models import TourOperator
from django.utils.text import slugify 

class Command(BaseCommand):
    help = 'Fix all tour operator slugs'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
            return
        ops = TourOperator.objects.all()
        for o in ops:
            
            #empty slug
            if not o.slug or o.slug == '':
                if o.name:
                    newslug = slugify(o.name)
                else:
                    newslug = slugify(o.pk)
                existent = TourOperator.objects.filter(slug=newslug)
                if existent.exists():
                    newslug = slugify('{} {}'.format(o.pk, newslug))
                o.slug = newslug
                print('empty {}:{}'.format(o.name, o.slug))
                o.save()

            #duplicated
            existent = TourOperator.objects.filter(slug=o.slug)
            existent = existent.exclude(pk=o.pk)
            if existent.exists():
                newslug = slugify('{} {}'.format(o.pk, o.name))
                o.slug = newslug
                print('existent {}:{}'.format(o.name, o.slug))
                o.save()
        self.stdout.write(self.style.SUCCESS("DONE"))
