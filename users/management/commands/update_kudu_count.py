from django.core.management.base import BaseCommand, CommandError
from photos.models import *
from reviews.models import *
from blog.models import *
from analytics import *


class Command(BaseCommand):
    help = 'Update kudu count field'

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
            photo.kudu_count = Action.objects.filter(action_type='K', photo__id=photo.id).count()
            photo.save()
            processed += 1

    def process_articles(self):
        article_count = Article.objects.count()
        processed = 0
        
        for article in Article.objects.all():
            percentage = processed / article_count * 100.0
            print ("processing article with id %d (%.2f%%)" % (article.id, percentage))
            article.kudu_count = Action.objects.filter(action_type='K', articles__id=article.id).count()
            article.save()
            processed += 1

    def process_tour_operator_reviews(self):
        review_count = TourOperatorReview.objects.count()
        processed = 0
        
        for review in TourOperatorReview.objects.all():
            percentage = processed / review_count * 100.0
            print ("processing tour operator review with id %d (%.2f%%)" % (review.id, percentage))
            review.kudu_count = Action.objects.filter(action_type='K', tour_operator_review__id=review.id).count()
            review.save()
            processed += 1
            
    def process_park_reviews(self):
        review_count = ParkReview.objects.count()
        processed = 0
        
        for review in ParkReview.objects.all():
            percentage = processed / review_count * 100.0
            print ("processing park review with id %d (%.2f%%)" % (review.id, percentage))
            review.kudu_count = Action.objects.filter(action_type='K', park_review__id=review.id).count()
            review.save()
            processed += 1
            
