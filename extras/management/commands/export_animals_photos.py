from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from photos.models import Photo
from places.models import Animal
from django.core.files import File
import MySQLdb
from PIL import Image
from django.db.models import Count
from shutil import copyfile
import os

class Command(BaseCommand):
    help = 'Export animals photos in /media/images/animals_ordered/'

    def add_arguments(self, parser):
        parser.add_argument('-outdir', required=True, type=str)
        parser.add_argument('-output', required=True, type=str)

    def handle(self, *args, **options):
        # not allowed in production
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
        animals = Animal.objects.all()
        animals_names = [x.name for x in animals]
        # annotate(animals_photos=Count('animals')).filter(animals_photos__gt=0)
        photos = Photo.objects.all()
        total_photos = photos.count()
        processed = 0
        res_table = []
        res_table.append(["filename"] + animals_names)
        photos_save = []
        for photo in photos:
            try:
                _ = photo.image.file.name
            except FileNotFoundError:
                print(photo.image.name,"does not exists")
                continue
            except ValueError:
                print(photo.image.name,"does not exists")
                continue
            if not photo.animals.exists():
                print(photo.image.name,"does not have animals")
                photo.image.file.close()
                continue
            if photo.animals.count() > 2:
                print(photo.image.name,"has more than 2 animals")
                photo.image.file.close()
                continue
            print(photo.image.name)
            res_row = []
            res_row.append(photo.image.name)
            photo.image.file.close()
            for animal_name in animals_names:
                if animal_name in [x.name for x in photo.animals.all()]:
                    res_row.append("1")
                else:
                    res_row.append("0")
            res_table.append(res_row)
            photos_save.append(photo)
            processed += 1
        with open(options['output'], 'w') as f:
            for _list in res_table:
                f.write(",".join(_list) + "\n")
        for photo in photos_save:
            original_path = photo.image.file.name
            dest_path = options['outdir'] + photo.image.name
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            copyfile(original_path, dest_path)
            photo.image.file.close()
        
        message = '%i/%i photos' % (processed, total_photos)
        self.stdout.write(self.style.SUCCESS(message))
