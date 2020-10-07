from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from reviews.models import TourOperatorReview, ParkReview
from analytics.models import Analytic, Action
from blog.models import Article
from places.models import Animal, Activity, Park
from photos.models import Photo
from django.contrib.auth.models import User
from django.core.files import File
import MySQLdb
from django.utils.timezone import make_aware


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
        photos = Photo.objects.filter(park_review__isnull=False)
        for photo in photos:
            photo.park_review = None
            photo.save()
        ParkReview.objects.all().delete()
        #parkreview
        cursor.execute("""
        SELECT
            park.park_name,
            user.email_address,
            parkreview.*,
            user.id as user_id
        FROM
            parkreview,
            park,
            user
        WHERE
            park.id = parkreview.park_id AND
            user.id = parkreview.user_id
        """)
        result = cursor.fetchall()
        for c in result:
            newdict = {}
            newdict['title'] = c.pop('review_title')
            newdict['slug'] = c.pop('review_title_slugged')[:255]
            newdict['content'] = c.pop('review_copy')
            newdict['pearls_of_wisdom'] = c.pop('pearls_of_wisdom')
            newdict['rejection_text'] = c.pop('rejection_text')
            newdict['friend_recommend'] = c.pop('friend_recommend') == 'Yes'
            newdict['days_booked'] = c.pop('days_booked')
            newdict['email_sent'] = c.pop('email_sent') == '1'
            newdict['overall_rating'] = c.pop('overall_rating')
            newdict['quality_wildlife_rating'] = c.pop('quality_wildlife_rating')
            newdict['quality_lodging_rating'] = c.pop('quality_lodging_rating')
            newdict['crowdedness_rating'] = c.pop('crowdedness_rating')
            newdict['book_lodging'] = c.pop('book_lodging') == 'Yes'
            
            date_created = c.pop('date_created')
            if date_created:
                date_created = make_aware(date_created)
            newdict['date_created'] = date_created
            
            date_modified = c.pop('date_modified')
            if date_modified:
                date_modified = make_aware(date_modified)
            newdict['date_modified'] = date_modified

            date_deleted = c.pop('date_deleted')
            if date_deleted:
                date_deleted = make_aware(date_deleted)
            newdict['date_deleted'] = date_deleted

            visit_date = c.pop('visit_date')
            newdict['visit_date'] = visit_date
            newdict['user'] = User.objects.get(username=c.pop('email_address'))
            newdict['park'] = Park.objects.get(name=c.pop('park_name'))
            exists_slug = ParkReview.objects.filter(slug=newdict['slug'])
            if exists_slug:
                newdict['slug'] = newdict['slug'] + '-' + str(c.pop('user_id'))

            status = c.pop('status')
            if status == "active":
                newdict['status'] = ParkReview.ACTIVE
            if status == "pending":
                newdict['status'] = ParkReview.PENDING
            if status == "rejected":
                newdict['status'] = ParkReview.REJECTED
                
            obj = ParkReview(**newdict)
            obj.save()
            created += 1
            
            SQL = "SELECT uuid FROM photo where album_id = %i"
            cursor.execute(SQL % c['album_id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                try:
                    photo = Photo.objects.get(uuid_value=c_['uuid'])
                    photo.park_review = obj
                    photo.save()
                except Photo.DoesNotExist:
                    pass
            #parkreview_activity
            SQL = """
            select activity.activity_name
            FROM
            parkreview_activity, activity
            WHERE
            parkreview_activity.activity_id = activity.id AND
            parkreview_activity.parkreview_id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                animal = Activity.objects.get(name_old=c_['activity_name'])
                obj.activities.add(animal)

            # parkreview_animal
            SQL = """
            select animal.animal_name
            FROM
            parkreview_animal, animal
            WHERE
            parkreview_animal.animal_id = animal.id AND
            parkreview_animal.parkreview_id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                animal = Animal.objects.get(name=c_['animal_name'])
                obj.animals.add(animal)

            #parkreviewvisit
            cursor.execute("""
            SELECT 
                parkreviewvisit.*, 
                user.email_address as email_address
            FROM
                parkreviewvisit 
                LEFT JOIN user ON user.id = parkreviewvisit.user_id
            WHERE
                parkreviewvisit.parkreview_id = %s
            """ % c['id'])
            result = cursor.fetchall()
            for c_ in result:
                newdict = {}
                newdict['date_created'] = make_aware(c_.pop('timestamp'))
                newdict['ip_address'] = c_.pop('ip_address')
                newdict['referer'] = c_.pop('referer')
                newdict['country_short'] = c_.pop('country_code')
                newdict['content_object'] = obj
                newdict['activity_type'] = 'CLICK'
                email_add = c_.pop('email_address')
                if email_add != None:
                    newdict['user'] = User.objects.get(username=email_add)
                obj_analitics = Analytic(**newdict)   
                obj_analitics.save()

            #parkreviewhelpful
            cursor.execute("""
            SELECT 
                parkreviewhelpful.timestamp,
                user.email_address as email_address
            FROM
                parkreviewhelpful
                LEFT JOIN user ON user.id = parkreviewhelpful.user_id
            WHERE
                parkreviewhelpful.parkreview_id = %s
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


        message = 'Imported %i updated %i parkreviews' % (created, updated)

        self.stdout.write(self.style.SUCCESS(message))
