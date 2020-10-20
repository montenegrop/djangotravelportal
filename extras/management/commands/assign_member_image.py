from django.core.management.base import BaseCommand, CommandError
from core.models import MediaFile
from django.contrib.auth.models import User
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
        users = User.objects.filter(is_active=True).filter(profile__avatar='')[:20]
        pics = MediaFile.objects.filter(name__contains='avatar')
        for user in users:
            if pics.exists():
                pic = pics.order_by('?')[0]
                user.profile.avatar = pic.image 
                user.profile.save()
        self.stdout.write(self.style.SUCCESS("UPDATED {}".format(users.count())))