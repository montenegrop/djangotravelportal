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


class Command(BaseCommand):
    help = 'Import ads'

    def add_arguments(self, parser):
        parser.add_argument('-db_host', required=True, type=str)
        parser.add_argument('-db_name', required=True, type=str)
        parser.add_argument('-db_user', required=True, type=str)
        parser.add_argument('-db_pass', required=True, type=str)
        parser.add_argument('-base_location', required=True, type=str)

    def handle(self, *args, **options):
        # not allowed in production
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
        db = MySQLdb.connect(
            host=options['db_host'], db=options['db_name'], user=options['db_user'], password=options['db_pass'])
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        created, updated = 0, 0
        cursor.execute("""
        select
            pagesponsor.* , touroperator.name as touroperator_name,
            touroperatoritinerary.itinerary_title as itinerary_name,
            photo.uuid as photo_uuid
        from
            pagesponsor
                LEFT JOIN touroperator ON pagesponsor.touroperator_id = touroperator.id
                LEFT JOIN touroperatoritinerary ON pagesponsor.touroperatoritinerary_id = touroperatoritinerary.id
                LEFT JOIN photo ON pagesponsor.photo_id = photo.id
        """)
        result = cursor.fetchall()
        for c in result:
            newdict = {}
            obj_id = c.pop('id')
            newdict['title'] = c.pop('ad_title')

            newdict['ad_type'], dummy = AdType.objects.get_or_create(
                name=c.pop('ad_type'))

            newdict['ad_location'], dummy = AdLocation.objects.get_or_create(
                name=c.pop('ad_location'))
            
            newdict['ad_banner'], dummy = AdBanner.objects.get_or_create(
                name=c.pop('ad_banner'))

            tour_operator = TourOperator.objects.get(
                name=c.pop('touroperator_name'))
            try:
                title = c.pop('itinerary_name')
                newdict['itinerary'] = Itinerary.objects.get(
                    title=title, tour_operator=tour_operator)
            except ObjectDoesNotExist:
                pass
            try:
                uuid = c.pop('photo_uuid')
                newdict['photo'] = Photo.objects.get(uuid=uuid)
            except ObjectDoesNotExist:
                pass
            date_modified = c.pop('date_modified')
            if date_modified:
                date_modified = make_aware(datetime.combine(
                    date_modified, datetime.min.time()))
            newdict['date_modified'] = date_modified

            date_start = c.pop('start_date')
            if date_start:
                date_start = make_aware(datetime.combine(date_start, datetime.min.time()))
            newdict['date_start'] = date_start

            date_end = c.pop('end_date')
            if date_end:
                date_end = make_aware(datetime.combine(date_end, datetime.min.time()))
            newdict['date_end'] = date_end

            date_created = c.pop('date_created')
            if date_created:
                date_created = make_aware(datetime.combine(
                    date_created, datetime.min.time()))
            newdict['date_created'] = date_created

            date_deleted = c.pop('date_deleted')
            if date_deleted:
                date_deleted = make_aware(datetime.combine(
                    date_deleted, datetime.min.time()))
            newdict['date_deleted'] = date_deleted

            
            obj, is_created = Ad.objects.update_or_create(
                title=newdict.pop('title'),
                tour_operator=tour_operator,
                defaults=newdict
            )
            if is_created:
                created += 1
            else:
                updated += 1
                obj.image.delete(save=True)
            if c['image_path']:
                image_path = '%sroot/%s' % (
                    options['base_location'], c['image_path'],)
                image_file = open(image_path, "rb")
                obj.image.save("image_%s" %
                               obj.pk, File(image_file), save=True)

            SQL = """
            SELECT countryindex.country_name
            FROM pagesponsor_countryindex, countryindex
            WHERE
            pagesponsor_countryindex.countryindex_id = countryindex.id AND
            pagesponsor_countryindex.pagesponsor_id = %s
            """
            cursor.execute(SQL % obj_id)
            result_ = cursor.fetchall()
            for c_ in result_:
                countryindex = CountryIndex.objects.get(
                    name=c_['country_name'])
                obj.country_indexes.add(countryindex)
            obj.save()
        message = 'Imported %i updated %i ads' % (created, updated)

        self.stdout.write(self.style.SUCCESS(message))
