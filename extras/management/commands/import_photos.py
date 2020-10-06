from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from places.models import Airline, Country, Park, CountryIndex, Animal, Activity
from photos.models import Photo, Comment
from operators.models import TourOperator
from django.conf import settings
from analytics.models import Action
from django.core.files import File
from photos.models import Tag
import MySQLdb
from analytics.models import Analytic
from django.contrib.auth.models import User
from django.utils.timezone import make_aware
import os.path
from django.core.exceptions import ObjectDoesNotExist
from shutil import copyfile
import sys
import hashlib
from datetime import datetime
from django.utils import timezone
import pytz


class Command(BaseCommand):
    help = 'Import photos'

    def add_arguments(self, parser):
        parser.add_argument('-db_host', required=True, type=str)
        parser.add_argument('-db_name', required=True, type=str)
        parser.add_argument('-db_user', required=True, type=str)
        parser.add_argument('-db_pass', required=True, type=str)
        parser.add_argument('-base_location', required=True, type=str)

    def handle(self, *args, **options):
        # not allowed in production
        users = {}
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
        db = MySQLdb.connect(
            host=options['db_host'], db=options['db_name'], user=options['db_user'], password=options['db_pass'])
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        created, updated = 0, 0
        cursor.execute("select COUNT(*) as count FROM photo")
        r = cursor.fetchone()
        count = r['count']
        Photo.objects.all().delete()
        cursor.execute("""select 
        photo.*,
        touroperator.name as tour_operator,
        countryindex.country_name as countryindex,
        park.park_name as park,
        activity.activity_name as activity,
        email_address
        from 
        photo 
        LEFT JOIN touroperator ON photo.touroperator_id = touroperator.id
        LEFT JOIN user ON user.id = photo.user_id
        LEFT JOIN countryindex ON photo.countryindex_id = countryindex.id
        LEFT JOIN park ON photo.park_id = park.id
        LEFT JOIN activity ON photo.activity_id = activity.id
        """)
        result = cursor.fetchall()
        skipped = 0
        smaller = 0
        hashes = {}
        for c in result:
            tour_operator_name = c['tour_operator']
            tour_operator_obj = False
            if tour_operator_name:
                try:
                    tour_operator_obj = TourOperator.objects.get(
                        name=tour_operator_name)
                except ObjectDoesNotExist:
                    print('Tour ' + str(c['tour_operator']) + 'doesnotexists')
                    continue
            username = c.pop('email_address')
            try:
                user = User.objects.get(username=username)
            except ObjectDoesNotExist:
                user = None
                pass
            newdict = {}
            newdict['uuid_value'] = c.pop('uuid')
            if not newdict['uuid_value']:
                print("UUID is null", c.pop("id"))
                continue
            newdict['caption'] = c.pop('caption')
            newdict['date_created'] = make_aware(c.pop('date_created'))
            newdict['user'] = user
            date_modified = c.pop('date_modified')
            if date_modified:
                date_modified = make_aware(date_modified)
            newdict['date_modified'] = date_modified
            if tour_operator_obj:
                newdict['tour_operator'] = tour_operator_obj
            if c['countryindex']:
                newdict['country_index'] = CountryIndex.objects.get(
                    name=c.pop('countryindex'))
            if c['park']:
                newdict['park'] = Park.objects.get(
                    name=c.pop('park'))
            if c['activity']:
                newdict['activity'] = Activity.objects.get(
                    name_old=c.pop('activity'))
            uuid = newdict.pop('uuid_value')
            print(uuid)
            obj, is_created = Photo.objects.update_or_create(
                uuid_value=uuid, defaults=newdict
            )
            if is_created:
                created += 1
            else:
                # obj.image.delete(save=True)
                print('updated')
                updated += 1
            #idk why uuid is changed
            obj.uuid_value = uuid
            tags = c['tags']
            if tags != None and tags != '':
                tags = tags.split(',')
                for tag in tags:
                    if tag != '':
                        o_tag, _ = Tag.objects.update_or_create(name=tag[:999])
                        obj.tags.add(o_tag)

            if c['gallery_path']:
                cur_image_path = '%sroot%s' % (
                    options['base_location'], c['gallery_path'],)
                
                if os.path.exists(cur_image_path):
                    filename, file_extension = os.path.splitext(cur_image_path)
                    openedFile = open(cur_image_path, 'rb')
                    readFile = openedFile.read()
                    md5Hash = hashlib.md5(readFile)
                    md5Hashed = md5Hash.hexdigest()
                    if md5Hashed in hashes:
                        skipped += 1
                        print('uuid duplicated file ' + str(obj.uuid_value))
                        obj.date_deleted = timezone.now()
                    hashes[md5Hashed] = 1

                    month = newdict['date_created'].month
                    year = newdict['date_created'].year
                    image_path = "/images/photos/%s/%s/" % (year, month)
                    os.makedirs(settings.MEDIA_ROOT +
                                image_path, exist_ok=True)
                    image_path += ("image_%d%s" %
                                   (obj.id, file_extension.lower()))
                    dst_image_path = settings.MEDIA_ROOT + image_path
                    copyfile(cur_image_path, dst_image_path)
                    obj.image = image_path[1:]
            if obj.image.width < 300 and obj.image.height < 300:
                smaller += 1
                print("image %s is skipped by its size %d ,%d" %
                      (obj.image, obj.image.width, obj.image.height))
                continue
            SQL = """
            select animal.animal_name
            FROM
            photo_animal, animal
            WHERE
            photo_animal.animal_id = animal.id AND
            photo_animal.photo_id = '%i'
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                animal = Animal.objects.get(name=c_['animal_name'])
                obj.animals.add(animal)



            # comments
            cursor.execute("""
            SELECT
                photocomment.*, user.email_address as email_address
            FROM
                photocomment
                LEFT JOIN user ON user.id = photocomment.user_id
            WHERE
                photocomment.photo_id = '%i'
            """ % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                Comment.objects.filter(content_type__model='Photo').delete()
                comment = Comment()
                comment.comment = c_.pop('photo_comment')
                email_add = c_.pop('email_address')
                try:
                    user = User.objects.get(username=email_add)
                except ObjectDoesNotExist:
                    print("User" + email_add + "dont exists")
                    continue
                comment.user = user
                comment.date_created = make_aware(c_.pop('timestamp'))
                comment.content_object = obj
                comment.save()

            # photo kudus
            cursor.execute("""
            SELECT 
                photolike.timestamp,
                user.email_address as email_address
            FROM
                photolike
                LEFT JOIN user ON user.id = photolike.user_id
            WHERE
                photolike.photo_id = %s
            """ % c['id'])
            result = cursor.fetchall()
            for c_ in result:
                newdict_ = {}
                newdict_['content_object'] = obj
                newdict_['date_created'] = make_aware(c_.pop('timestamp'))
                newdict_['action_type'] = Action.KUDU
                email_add = c_.pop('email_address')
                if email_add != None:
                    newdict_['user'] = User.objects.get(username=email_add)
                obj_act = Action(**newdict_)
                obj_act.save()
            obj.save()

            # photovisit
            SQL = """
            SELECT 
                photovisit.*, photo.uuid, user.email_address as email_address,
                photovisit.user_id
            FROM
                photo, photovisit
                LEFT JOIN user ON user.id = photovisit.user_id
            WHERE
                photovisit.photo_id = photo.id
                AND photo.uuid = '%s'
            """
            cursor.execute(SQL % uuid)
            result_ = cursor.fetchall()
            for c_ in result_:
                analytic = Analytic()
                analytic.content_object = obj
                analytic.date_created = make_aware(c_.pop('timestamp'))
                analytic.ip_address = c_.pop('ip_address')
                analytic.referer = c_.pop('referer')
                #analytic.country_code = c_.pop('country_code')
                analytic.activity_type = 'VISIT'
                email_add = c_.pop('email_address')
                if email_add != None:
                    if not email_add in users:
                        try:
                            users[email_add] = User.objects.get(
                                username=email_add)
                            analytic.user = users[email_add]
                        except ObjectDoesNotExist:
                            print("User" + email_add + "dont exists")
                    else:
                        analytic.user = users[email_add]
                    analytic.save()
            obj.save()
        message = 'Imported %i updated %i skipped %i (%i by size) photos' % (
            created, updated, skipped, smaller)

        self.stdout.write(self.style.SUCCESS(message))
