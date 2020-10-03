from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from places.models import Activity, Animal, Park, CountryIndex
from django.utils import timezone
from analytics.models import Action, Analytic
from photos.models import Comment
from bs4 import BeautifulSoup as bs

class Category(models.Model):
    name = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    homepage_text = models.CharField(max_length=300)
    description = models.CharField(max_length=300)
    hidden = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Article(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    categories = models.ManyToManyField(Category, blank=True)
    activities = models.ManyToManyField(Activity, blank=True)
    animals = models.ManyToManyField(Animal, blank=True)
    parks = models.ManyToManyField(Park, blank=True)
    country_indexes = models.ManyToManyField(CountryIndex, blank=True)
    title = models.CharField(max_length=700)
    title_short = models.CharField(max_length=300, blank=True, null=True)
    slug = models.SlugField(max_length=500)
    image = models.ImageField(upload_to='images/articles/%Y/%m/%d', blank=True, null=True)
    image_raw = models.ImageField(upload_to='images/articles_raw/%Y/%m/%d', blank=True, null=True)
    image_caption = models.CharField(max_length=1500, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    highlights = models.CharField(max_length=1500, blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    STATUS_DRAFT = "DRAFT"
    STATUS_PUBLISHED = "PUBLISHED"
    STATUS_TRASH = 'TRASH'
    ARTICLE_STATUS_CHOICES = (
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_TRASH, "Trash"),)
    article_status = models.CharField(max_length=15,
                                      choices=ARTICLE_STATUS_CHOICES,
                                      default="DRAFT")
    actions = GenericRelation(Action, related_query_name='articles')
    date_created = models.DateTimeField(default=timezone.now)
    meta_description = models.CharField(max_length=1500, blank=True, null=True)
    meta_keywords = models.CharField(max_length=700, blank=True, null=True)
    meta_title = models.CharField(max_length=700, blank=True, null=True)

    kudu_count = models.IntegerField(default=0)
    visit_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)

    def update_kudu_count(self):
        self.kudu_count = Action.objects.filter(action_type="K", articles=self).count()
        self.save()
        
    def update_comments_count(self):
        self.comment_count = self.comments().count()
        self.save()
        
    def update_visit_count(self):
        self.visit_count = Analytic.objects.filter(activity_type="VISIT", content_type__model="article", object_id = self.id).count()
        self.save()
    

    def excerpt(self, n=100):
        return (self.content[:n] + '...') if len(self.content) > n else self.content
    
    def comments(self):
        return Comment.objects.filter(content_type__model="article", object_id=self.id)
    
    def __str__(self):
        return self.title

    def content_no_script(self):
        soup = bs(self.content)
        [s.extract() for s in soup('script')]
        return soup


    
