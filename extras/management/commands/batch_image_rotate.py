from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from photos.models import Photo
from django.core.files import File
import MySQLdb
from PIL import Image
import imdirect


class Command(BaseCommand):
    help = 'Rotate all photos'

    def handle(self, *args, **options):
        # not allowed in production
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
        total = 0
        rotated = 0
        photos = Photo.objects.all()
        for photo in photos:
            print(settings.MEDIA_ROOT + photo.image.path)
            img = Image.open()
            print("{0}, Orientation: {1}".format(img, img._getexif().get(274)))
            img_rotated = imdirect.autorotate(img)
            total += 1
            if total == 10:
                break
        message = 'Rotated %i of %i photos' % (rotated, total)
        self.stdout.write(self.style.SUCCESS(message))
