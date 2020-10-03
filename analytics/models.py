from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class Analytic(models.Model):
    VISIT = 'VISIT'
    CLICK = 'CLICK'
    ACTIVITY_TYPE = (
        (VISIT, "Visit"),
        (CLICK, "Click"),
    )
    activity_type = models.CharField(max_length=15,
                                     choices=ACTIVITY_TYPE,
                                     blank=True, null=True, db_index=True)
    user = models.ForeignKey(User, blank=True,
                             null=True, on_delete=models.PROTECT)
    date_created = models.DateTimeField(default=timezone.now)
    ip_address = models.CharField(max_length=300)
    device_type = models.CharField(max_length=300)
    browser_type = models.CharField(max_length=300)
    browser_version = models.CharField(max_length=300)
    os_type = models.CharField(max_length=300)
    os_version = models.CharField(max_length=300)
    referer = models.TextField(blank=True, null=True)
    path = models.CharField(max_length=350,blank=True, null=True)
    country_short = models.CharField(max_length=20,blank=True, null=True)
    page_url = models.URLField(blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,blank=True, null=True)
    object_id = models.PositiveIntegerField(db_index=True,blank=True, null=True)
    content_object = GenericForeignKey()


class Action(models.Model):
    FAVORITE = 'F'
    KUDU = 'K'
    LIKE = 'L'
    UP_VOTE = 'U'
    DOWN_VOTE = 'D'
    HELPFUL = 'H'
    ACTION_CHOICES = (
        (FAVORITE, 'Favorite'),
        (KUDU, 'Kudu'),
        (LIKE, 'Like'),
        (UP_VOTE, 'Up Vote'),
        (DOWN_VOTE, 'Down Vote'),
        (HELPFUL, 'Helpful'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=1, choices=ACTION_CHOICES, db_index=True)
    date_created = models.DateTimeField(default=timezone.now)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='actions',null=True, blank=True)
    object_id = models.PositiveIntegerField(db_index=True,null=True, blank=True)
    content_object = GenericForeignKey()
