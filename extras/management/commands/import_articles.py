from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from analytics.models import Action
import os.path
from blog.models import Category
from django.core.files import File
import MySQLdb
from django.contrib.auth.models import User
from blog.models import Article,  Activity, Animal, Park
from photos.models import Comment
from places.models import CountryIndex
from django.utils.timezone import make_aware
from django.core.files.storage import FileSystemStorage
import requests # to get image from the web
from bs4 import BeautifulSoup

class Command(BaseCommand):
    help = 'Import articles'

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
        db = MySQLdb.connect(host=options['db_host'], db=options['db_name'], user=options['db_user'], password=options['db_pass'], charset='utf8', use_unicode=True,)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        created, updated = 0, 0
        comments = 0
        cursor.execute("""
        select article.*, user.email_address as user_email, articlecategory.name as category_name from
        article, user, articlecategory
        WHERE
        article.user_id = user.id AND
        article.category_id = articlecategory.id
        """)
        Comment.objects.filter(content_type__model='article').delete()
        result = cursor.fetchall()
        for c in result:
            newdict = {}
            newdict['title'] = c.pop('title')
            newdict['title_short'] = c.pop('title_short')
            newdict['highlights'] = c.pop('highlights')
            newdict['content'] = c.pop('article_copy')
            newdict['source'] = c.pop('source')
            newdict['image_caption'] = c.pop('image_caption')
            newdict['slug'] = c.pop('title_slugged')[:499]
            if c['status'] == 'active':
                newdict['article_status'] = 'PUBLISHED'
            if c['status'] == 'pending':
                newdict['article_status'] = 'DRAFT'
            newdict['date_created'] = make_aware(c.pop('date_created'))
            newdict['meta_title'] = c.pop('meta_title')
            newdict['meta_keywords'] = c.pop('meta_keywords')
            newdict['meta_description'] = c.pop('meta_description')

            newdict['user'] = User.objects.get(email=c['user_email'])
            category_name = c.pop('category_name')
            obj, is_created = Article.objects.update_or_create(
                title=newdict.pop('title'), defaults=newdict
            )

            #search all images
            soup = BeautifulSoup(obj.content)
            imgs = soup.findAll("img",{"alt":True, "src":True})
            for img in imgs:
                img_url = img["src"]
                print(img_url)
                filename = img_url.split("/")[-1]
                r = requests.get(img_url, stream = True)
                if r.status_code == 200:
                    # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
                    r.raw.decode_content = True
                    #save the image in the django media dir
                    filename = 'uploads/imported_articles/%s' % filename
                    fs = FileSystemStorage()
                    filename = fs.save(filename, r.raw)
                    uploaded_file_url = fs.url(filename)
                    obj.content = obj.content.replace(img_url,uploaded_file_url)
                    print(uploaded_file_url)
                    print('*')
            obj.save()
            
            obj.date_created = newdict['date_created']
            if is_created:
                created += 1
            else:
                obj.image.delete(save=True)
                updated += 1
            obj.categories.set([Category.objects.get(name=category_name)])
            if c['image_path']:
                image_path = '%sroot/%s' % (
                    options['base_location'], c['image_path'],)
                if os.path.exists(image_path):
                    image_file = open(image_path, "rb")
                    obj.image.save("image_%s" %
                                   obj.pk, File(image_file), save=True)
       
            
            if c['image_raw']:
                image_raw_path = '%sroot/%s' % (
                    options['base_location'], c['image_raw'],)
                if os.path.exists(image_raw_path):
                    image_raw_file = open(image_raw_path, "rb")
                    obj.image_raw.save("image_%s" %
                                   obj.pk, File(image_raw_file), save=True)

            SQL = """
            select activity.activity_name
            FROM
            article_activity, activity
            WHERE
            article_activity.activity_id = activity.id AND
            article_activity.article_id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                park = Activity.objects.get(name_old=c_['activity_name'])
                obj.activities.add(park)
            SQL = """
            select animal.animal_name
            FROM
            article_animal, animal
            WHERE
            article_animal.animal_id = animal.id AND
            article_animal.article_id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                park = Animal.objects.get(name=c_['animal_name'])
                obj.animals.add(park)
            SQL = """
            select countryindex.country_name
            FROM
            article_countryindex, countryindex
            WHERE
            article_countryindex.countryindex_id = countryindex.id AND
            article_countryindex.article_id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                country_index = CountryIndex.objects.get(
                    name=c_['country_name'])
                obj.country_indexes.add(country_index)
            SQL = """
            select park.park_name
            FROM
            article_park, park
            WHERE
            article_park.park_id = park.id AND
            article_park.article_id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                country_index = Park.objects.get(name=c_['park_name'])
                obj.parks.add(country_index)
            SQL = """
            select articlecomment.*, user.email_address
            FROM
            articlecomment, user
            WHERE
            user.id = articlecomment.user_id AND
            articlecomment.article_id = %i
             """
            cursor.execute(SQL % c['id'])
            result_ = cursor.fetchall()
            for c_ in result_:
                comment = Comment()
                user = User.objects.get(email=c_['email_address'])
                if not user:
                    print('in articles, ' + c_['email_address'] + ' user does not exists')
                    continue
                comment.user = user
                comment.content_object = obj
                comment.comment = c_['comment']
                comment.date_created = make_aware(c_.pop('timestamp'))
                comment.save()
                comments += 1

            #article kudus
            cursor.execute("""
            SELECT 
                articlekudu.timestamp,
                user.email_address as email_address
            FROM
                articlekudu
                LEFT JOIN user ON user.id = articlekudu.user_id
            WHERE
                articlekudu.article_id = %s
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
        message = 'Imported %i updated %i articles and %i comments' % (
            created, updated, comments)
        self.stdout.write(self.style.SUCCESS(message))
