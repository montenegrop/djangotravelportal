from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from analytics.models import Analytic
from operators.models import Itinerary, ItineraryExtra, ItineraryType, TourOperator
from blog.models import Article
from django.contrib.auth.models import User
from django.core.files import File
import MySQLdb
from django.utils.timezone import make_aware
from places.models import CountryIndex, Park
from ads.models import Ad, AdLocation, AdType
import datetime
from places.models import CountryIndex

class Command(BaseCommand):
    help = 'Import analytics'

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
        Analytic.objects.all().delete()

        # articlevisit
        cursor.execute("""
        SELECT
            articlevisit.*, article.title as title, user.email_address as email_address,
            articlevisit.user_id
        FROM
            article, articlevisit
            LEFT JOIN user ON user.id = articlevisit.user_id
        WHERE
            articlevisit.article_id = article.id
        """)
        result = cursor.fetchall()
        for c in result:
            analytic = Analytic()
            analytic.date_created = make_aware(c.pop('timestamp'))
            analytic.ip_address = c.pop('ip_address')
            analytic.referer = c.pop('referer')
            analytic.country_short = c.pop('country_code')
            analytic.content_object = Article.objects.get(
                title=c.pop('title'))
            analytic.activity_type = 'VISIT'
            email_add = c.pop('email_address')
            if email_add != None:
                analytic.user = User.objects.get(username=email_add)
            analytic.save()
            created += 1

        # countryindexvisit
        cursor.execute("""
        SELECT
            countryindexvisit.*, countryindex.country_name as country_name, user.email_address as email_address,
            countryindexvisit.user_id
        FROM
            countryindex, countryindexvisit
            LEFT JOIN user ON user.id = countryindexvisit.user_id
        WHERE
            countryindexvisit.countryindex_id = countryindex.id
        ORDER BY
            countryindexvisit.id DESC LIMIT 10000
        """)
        result = cursor.fetchall()
        for c in result:
            analytic = Analytic()
            analytic.date_created = make_aware(c.pop('timestamp'))
            analytic.ip_address = c.pop('ip_address')
            analytic.referer = c.pop('referer')
            analytic.country_short = c.pop('country_code')
            analytic.content_object = CountryIndex.objects.get(
                name=c.pop('country_name'))
            analytic.activity_type = 'VISIT'
            email_add = c.pop('email_address')
            if email_add != None:
                analytic.user = User.objects.get(username=email_add)
            analytic.save()
            created += 1

         # pagesponsorvisit
        cursor.execute("""
        SELECT
            pagesponsorvisit.*, 
            pagesponsor.ad_title as ad_title,
            pagesponsor.date_modified as ad_date_modified,
            pagesponsor.touroperator_id as touroperator_id,
            user.email_address as email_address,
            pagesponsorvisit.user_id
        FROM
            pagesponsor, pagesponsorvisit
            LEFT JOIN user ON user.id = pagesponsorvisit.user_id
        WHERE
            pagesponsorvisit.pagesponsor_id = pagesponsor.id
        ORDER BY
            pagesponsorvisit.id DESC LIMIT 10000
        """)
        result = cursor.fetchall()
        for c in result:
            analytic = Analytic()
            analytic.date_created = make_aware(c.pop('timestamp'))
            analytic.ip_address = c.pop('ip_address')
            analytic.referer = c.pop('referer')
            analytic.country_short = c.pop('country_code')

            date_modified = c.pop('ad_date_modified')
#            if date_modified:
#                date_modified = make_aware(datetime.combine(
#                    date_modified, datetime.min.time()))

            ad = Ad.objects.filter(title=c.pop('ad_title')).filter(
                date_modified=date_modified).first()
            if ad:
                analytic.content_object = ad
                analytic.activity_type = 'VISIT'
                email_add = c.pop('email_address')
                if email_add != None:
                    analytic.user = User.objects.get(username=email_add)
                analytic.save()
            created += 1

        # pagesponsorclick
        cursor.execute("""
        SELECT
            pagesponsorclick.*, pagesponsor.ad_title as ad_title,
            pagesponsor.touroperator_id as touroperator_id,
            user.email_address as email_address,
            pagesponsorclick.user_id
        FROM
            pagesponsor, pagesponsorclick
            LEFT JOIN user ON user.id = pagesponsorclick.user_id
        WHERE
            pagesponsorclick.pagesponsor_id = pagesponsor.id
        ORDER BY
            pagesponsorclick.id DESC LIMIT 10000
        """)
        result = cursor.fetchall()
        for c in result:
            analytic = Analytic()
            analytic.date_created = make_aware(c.pop('timestamp'))
            analytic.ip_address = c.pop('ip_address')
            analytic.referer = c.pop('referer')
            analytic.country_short = c.pop('country_code')
            analytic.content_object = Ad.objects.filter(
                title=c.pop('ad_title')).first()
            analytic.activity_type = 'CLICK'
            email_add = c.pop('email_address')
            if email_add != None:
                analytic.user = User.objects.get(username=email_add)
            analytic.save()
            created += 1

        # parkvisit
        cursor.execute("""
        SELECT
            parkvisit.*, park.park_name, user.email_address as email_address,
            parkvisit.user_id
        FROM
            park, parkvisit
            LEFT JOIN user ON user.id = parkvisit.user_id
        WHERE
            parkvisit.park_id = park.id
        ORDER BY
            parkvisit.id DESC LIMIT 10000
        """)
        result = cursor.fetchall()
        for c in result:
            analytic = Analytic()
            analytic.date_created = make_aware(c.pop('timestamp'))
            analytic.ip_address = c.pop('ip_address')
            analytic.referer = c.pop('referer')
            analytic.country_short = c.pop('country_code')
            analytic.content_object = Park.objects.get(
                name=c.pop('park_name'))
            analytic.activity_type = 'VISIT'
            email_add = c.pop('email_address')
            if email_add != None:
                analytic.user = User.objects.get(username=email_add)
            analytic.save()
            created += 1

        # touroperatoritineraryvisit
        cursor.execute("""
        SELECT
            touroperatoritineraryvisit.*, touroperatoritinerary.itinerary_title, user.email_address as email_address,
            touroperatoritineraryvisit.user_id, touroperatoritinerary.itinerary_title_slugged
        FROM
            touroperatoritinerary, touroperatoritineraryvisit
            LEFT JOIN user ON user.id = touroperatoritineraryvisit.user_id
        WHERE
            touroperatoritineraryvisit.touroperatoritinerary_id = touroperatoritinerary.id
        ORDER BY
            touroperatoritineraryvisit.id DESC LIMIT 10000
        """)
        result = cursor.fetchall()
        for c in result:
            analytic = Analytic()
            analytic.date_created = make_aware(c.pop('timestamp'))
            analytic.ip_address = c.pop('ip_address')
            analytic.referer = c.pop('referer')
            analytic.country_short = c.pop('country_code')
            analytic.content_object = Itinerary.objects.get(
                slug=c.pop('itinerary_title_slugged'))
            analytic.activity_type = 'VISIT'
            email_add = c.pop('email_address')
            if email_add != None:
                analytic.user = User.objects.get(username=email_add)
            analytic.save()
            created += 1

         # touroperatoritineraryvisit
        cursor.execute("""
        SELECT
            touroperatorvisit.*, touroperator.name_slugged, user.email_address as email_address
        FROM
            touroperator, touroperatorvisit
            LEFT JOIN user ON user.id = touroperatorvisit.user_id
        WHERE
            touroperatorvisit.touroperator_id = touroperator.id
        ORDER BY
            touroperatorvisit.id DESC LIMIT 10000
        """)
        result = cursor.fetchall()
        for c in result:
            analytic = Analytic()
            analytic.date_created = make_aware(c.pop('timestamp'))
            analytic.ip_address = c.pop('ip_address')
            analytic.referer = c.pop('referer')
            analytic.country_short = c.pop('country_code')
            analytic.content_object = TourOperator.objects.get(
                slug=c.pop('name_slugged'))
            analytic.activity_type = 'VISIT'
            email_add = c.pop('email_address')
            if email_add != None:
                analytic.user = User.objects.get(username=email_add)
            analytic.save()
            created += 1

        # uservisit
        cursor.execute("""
        SELECT 
            uservisit.*,
            u.email_address,
            u2.email_address as real_email_address
        FROM
            uservisit
            LEFT JOIN (SELECT id, email_address FROM user) as u ON u.id = uservisit.user_id
            LEFT JOIN (SELECT id, email_address FROM user) as u2 ON u2.id = uservisit.realuser_id
        ORDER BY
            uservisit.id DESC LIMIT 10000
        """)
        result = cursor.fetchall()
        for c in result:
            analytic = Analytic()
            analytic.date_created = make_aware(c.pop('timestamp'))
            analytic.ip_address = c.pop('ip_address')
            analytic.referer = c.pop('referer')
            analytic.country_short = c.pop('country_code')
            analytic.content_object = User.objects.get(
                email=c.pop('real_email_address'))
            analytic.activity_type = 'VISIT'
            email_add = c.pop('email_address')
            if email_add != None:
                analytic.user = User.objects.get(username=email_add)
            analytic.save()
            created += 1
        message = 'Imported %i updated %i analytics' % (created, updated)

        self.stdout.write(self.style.SUCCESS(message))
