from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from reviews.models import TourOperatorReview, ParkReview, SafariType
from analytics.models import Analytic, Action
from photos.models import Photo
from blog.models import Article
from places.models import Animal, Activity, Park, CountryIndex
from operators.models import TourOperator
from django.contrib.auth.models import User
from django.core.files import File
import MySQLdb
from django.utils.timezone import make_aware
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    help = 'Import reviews'

    def add_arguments(self, parser):
        parser.add_argument('-db_host', required=True, type=str)
        parser.add_argument('-db_name', required=True, type=str)
        parser.add_argument('-db_user', required=True, type=str)
        parser.add_argument('-db_pass', required=True, type=str)

    def handle(self, *args, **options):
        # not allowed in production
        if not settings.DEBUG:
            self.stdout.write(self.style.ERROR("DEBUG is off"))
        db = MySQLdb.connect(
            host=options['db_host'], db=options['db_name'], user=options['db_user'], password=options['db_pass'])
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        created, updated = 0, 0
        photos = Photo.objects.filter(tour_operator_review__isnull=False)
        for photo in photos:
            photo.park_review = None
            photo.save()
        TourOperatorReview.objects.all().delete()
        #touroperatorreview
        cursor.execute("""
        SELECT
            touroperator.name,
            user.email_address,
            user.id as user_id,
            touroperatorreview.*
        FROM
            touroperatorreview,
            touroperator,
            user
        WHERE
            touroperator.id = touroperatorreview.touroperator_id AND
            user.id = touroperatorreview.user_id
        """)
        result = cursor.fetchall()
        for c in result:
            newdict = {}
            newdict['title'] = c.pop('review_title')
            newdict['slug'] = c.pop('review_title_slugged')
            newdict['content'] = c.pop('review_copy')
            newdict['pearls_of_wisdom'] = c.pop('pearls_of_wisdom')
            newdict['email_sent'] = c.pop('email_sent') == '1'
            newdict['rejection_text'] = c.pop('rejection_text')
            newdict['friend_recommend'] = c.pop('friend_recommend') == 'Yes'
            newdict['overall_rating'] = c.pop('overall_rating')
            
            newdict['safari_type'], dymmy = SafariType.objects.get_or_create(name=c.pop('safari_type'))
            days_booked = c.pop('days_booked')
            if days_booked == '30+':
                days_booked = 30
            newdict['days_booked'] = days_booked
            newdict['did_not_go'] = c.pop('did_not_go_flag') != None
            newdict['vehicle_rating'] = c.pop('vehicle_rating')
            newdict['meet_and_greet_rating'] = c.pop('meet_and_greet_rating')
            newdict['responsiveness_rating'] = c.pop('responsiveness_rating')
            newdict['safari_quality_rating'] = c.pop('safari_quality_rating')
            newdict['itinerary_quality_rating'] = c.pop('itinerary_quality_rating')
            newdict['start_date'] = c.pop('start_date')


            newdict['response'] = c.pop('response')
            newdict['response_date'] = c.pop('response_date')
            newdict['response_email_sent'] = c.pop('response_email_sent')

            
            date_created = c.pop('date_created')
            if date_created:
                date_created = make_aware(date_created)
            newdict['date_created'] = date_created
            newdict['find_out'] = c.pop('find_out_about')
            
            date_modified = c.pop('date_modified')
            if date_modified:
                date_modified = make_aware(date_modified)
            newdict['date_modified'] = date_modified

            date_deleted = c.pop('date_deleted')
            if date_deleted:
                date_deleted = make_aware(date_deleted)
            newdict['date_deleted'] = date_deleted
            newdict['user'] = User.objects.get(username=c.pop('email_address'))
            try:
                newdict['tour_operator'] = TourOperator.objects.get(name=c['name'])
            except ObjectDoesNotExist:
                print('Tour ' + str(c['name']) + 'doesnotexists')
                continue
            exists_slug = TourOperatorReview.objects.filter(slug=newdict['slug'])
            if exists_slug:
                newdict['slug'] = newdict['slug'] + '-' + str(c.pop('user_id'))

            status = c.pop('status')
            if status == "active":
                newdict['status'] = TourOperatorReview.ACTIVE
            if status == "pending":
                newdict['status'] = TourOperatorReview.PENDING
            if status == "rejected":
                newdict['status'] = TourOperatorReview.REJECTED

            obj = TourOperatorReview(**newdict)

            obj.save()
            created += 1
            #touroperatorreview_activity
            SQL = """
            select activity.activity_name
            FROM
            touroperatorreview_activity, activity
            WHERE
            touroperatorreview_activity.activity_id = activity.id AND
            touroperatorreview_activity.touroperatorreview_id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                animal = Activity.objects.get(name_old=c_['activity_name'])
                obj.activities.add(animal)


            SQL = "SELECT uuid FROM photo where album_id = %i"
            cursor.execute(SQL % c['album_id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                try:
                    photo = Photo.objects.get(uuid_value=c_['uuid'])
                    photo.tour_operator_review = obj
                    photo.save()
                except Photo.DoesNotExist:
                    pass

            # touroperatorreview_animal
            SQL = """
            select animal.animal_name
            FROM
            touroperatorreview_animal, animal
            WHERE
            touroperatorreview_animal.animal_id = animal.id AND
            touroperatorreview_animal.touroperatorreview_id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                animal = Animal.objects.get(name=c_['animal_name'])
                obj.animals.add(animal)

            # touroperatorreview_park
            SQL = """
            select park.park_name
            FROM
            touroperatorreview_park, park
            WHERE
            touroperatorreview_park.park_id = park.id AND
            touroperatorreview_park.touroperatorreview_id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                park = Park.objects.get(name=c_['park_name'])
                obj.parks.add(park)
            
            # touroperatorreview_countryindex
            SQL = """
            select countryindex.country_name
            FROM
            touroperatorreview_countryindex, countryindex
            WHERE
            touroperatorreview_countryindex.countryindex_id = countryindex.id AND
            touroperatorreview_countryindex.touroperatorreview_id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                countri_index = CountryIndex.objects.get(name=c_['country_name'])
                obj.country_indexes.add(countri_index)

            #touroperatorreviewvisit
            #cursor.execute("""
            #SELECT 
            #    touroperatorreviewvisit.*,
            #    user.email_address as email_address
            #FROM
            #    touroperatorreviewvisit
            #    LEFT JOIN user ON user.id = touroperatorreviewvisit.user_id
            #WHERE
            #    touroperatorreviewvisit.touroperatorreview_id = %s
            #""" % c['id'])
            #result = cursor.fetchall()
            #for c_ in result:
            #    newdict = {}
            #    newdict['date_created'] = make_aware(c_.pop('timestamp'))
            #    newdict['ip_address'] = c_.pop('ip_address')
            #    newdict['referer'] = c_.pop('referer')
            #    newdict['country_short'] = c_.pop('country_code')
            #    newdict['content_object'] = obj
            #    newdict['activity_type'] = 'CLICK'
            #    email_add = c_.pop('email_address')
            #    if email_add != None:
            #        newdict['user'] = User.objects.get(username=email_add)
            #    obj_analitics = Analytic(**newdict)   
            #    obj_analitics.save()

            #touroperatorreviewhelpful
            cursor.execute("""
            SELECT 
                touroperatorreviewhelpful.timestamp,
                user.email_address as email_address
            FROM
                touroperatorreviewhelpful
                LEFT JOIN user ON user.id = touroperatorreviewhelpful.user_id
            WHERE
                touroperatorreviewhelpful.touroperatorreview_id = %s
            """ % c['id'])
            result = cursor.fetchall()
            for c_ in result:
                newdict = {}
                newdict['content_object'] = obj
                newdict['date_created'] = make_aware(c_.pop('timestamp'))
                newdict['action_type'] = Action.KUDU
                email_add = c_.pop('email_address')
                if email_add != None:
                    newdict['user'] = User.objects.get(username=email_add)
                obj_act = Action(**newdict)   
                obj_act.save()
            obj.save()

        #touroperatorreviewlead TODO what is it?

        message = 'Imported %i updated %i touroperatorreviews' % (created, updated)

        self.stdout.write(self.style.SUCCESS(message))
