from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from places.models import Animal
from django.core.files import File
from photos.models import Photo
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Predict animals presents in a picture file'
    def add_arguments(self, parser):
        parser.add_argument('-photo_path', required=True, type=str)

    def handle(self, *args, **options):
        try:
            image_path = os.path.join(options['photo_path'])
            img_array = cv2.imread(image_path)
            new_array = cv2.resize(img_array, (IMG_SIZE, IMG_SIZE))
        except Exception as e:
            print(image_path)
            print(e)
            return
        Y = []
        Y.append(new_array)
        weights.best.basic_cnn.hdf5
        