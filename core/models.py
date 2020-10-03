from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.utils import timezone
from operators.models import TourOperator

class EmailLog(models.Model):
    address_to = models.CharField(max_length=2000)
    address_from = models.CharField(max_length=2000)
    subject = models.CharField(max_length=2000)
    body = models.TextField()
    cc = models.CharField(max_length=2000, blank=True, null=True)
    bcc = models.CharField(max_length=2000, blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    date_opened = models.DateTimeField(blank=True, null=True)
    date_last_checked = models.DateTimeField(blank=True, null=True)
    date_clicked = models.DateTimeField(blank=True, null=True)
    date_last_clicked = models.DateTimeField(blank=True, null=True)

class MediaFile(models.Model):
    name = models.CharField(max_length=1000)
    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    image = models.ImageField(upload_to='images/mediafiles/%Y/%m/%d')
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

class MissingInfo(models.Model):
    WHAT_CHOICES = (
        ('PARK', 'Park or game reserve'),
        ('OPERATOR', 'Tour Operator'),
    )
    what_is_missing = models.CharField(max_length=10, choices=WHAT_CHOICES)
    name = models.CharField(max_length=400)
    email = models.EmailField(blank=True, null=True)
    how_did_you_hear = models.CharField(max_length=500)
    description = models.CharField(max_length=2000)

    def __str__(self):
        return self.name

class Page(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True)
    image = models.ImageField(upload_to='images/pages/%Y/%m/%d', blank=True, null=True)
    content = models.TextField()
    meta_description = models.CharField(max_length=1500, blank=True, null=True)
    meta_keywords = models.CharField(max_length=700, blank=True, null=True)
    meta_title = models.CharField(max_length=700, blank=True, null=True)

    def __str__(self):
        return self.title

    def parse_content(self):
        content = self.content
        content = content.replace("[% date.format(date.now, &#39;%Y&#39;, &#39;en_GB&#39;) -%]",'{{current_year}}')
        return content