from django.core.management.base import BaseCommand, CommandError
from photos.models import *
from reviews.models import *
from blog.models import *
from analytics import *


class Command(BaseCommand):
    help = 'Update visit count field'

    def handle(self, *args, **options):
        self.process_photos()
        self.process_articles()
        self.process_tour_operator_reviews()
        self.process_park_reviews()
        

    def process_photos(self):
        photo_count = Photo.objects.count()
        processed = 0
        
        for photo in Photo.objects.all():
            percentage = processed / photo_count * 100.0
            print ("processing photo with id %d (%.2f%%)" % (photo.id, percentage))
            photo.visit_count = Analytic.objects.filter(activity_type="VISIT", content_type__model="photo", object_id = photo.id).count()
            photo.save()
            processed += 1

    def process_articles(self):
        article_count = Article.objects.count()
        processed = 0
        
        for article in Article.objects.all():
            percentage = processed / article_count * 100.0
            print ("processing article with id %d (%.2f%%)" % (article.id, percentage))
            article.visit_count = Analytic.objects.filter(activity_type="VISIT", content_type__model="article", object_id = article.id).count()
            article.save()
            processed += 1
            article.comment_count = Comment.objects.filter(content_type__model="Article", object_id = article.id).count()
            
    def process_tour_operator_reviews(self):
        review_count = TourOperatorReview.objects.count()
        processed = 0
        
        for review in TourOperatorReview.objects.all():
            percentage = processed / review_count * 100.0
            print ("processing tour operator review with id %d (%.2f%%)" % (review.id, percentage))
            review.visit_count = Analytic.objects.filter(activity_type="VISIT", content_type__model="touroperatorreview", object_id = review.id).count()
            review.save()
            processed += 1
            
    def process_park_reviews(self):
        review_count = ParkReview.objects.count()
        processed = 0
        
        for review in ParkReview.objects.all():
            percentage = processed / review_count * 100.0
            print ("processing park review with id %d (%.2f%%)" % (review.id, percentage))
            review.visit_count = Analytic.objects.filter(activity_type="VISIT", content_type__model="parkreview", object_id = review.id).count()
            review.save()
            processed += 1
            
