from django.db import models
from operators.models import TourOperator, Itinerary
from photos.models import Photo
from places.models import CountryIndex
from django.utils import timezone


class AdType(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class AdLocation(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class AdBanner(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Ad(models.Model):
    title = models.CharField(max_length=300)
    ad_type = models.ForeignKey(AdType, on_delete=models.PROTECT)
    ad_location = models.ForeignKey(AdLocation, on_delete=models.PROTECT)
    ad_banner = models.ForeignKey(AdBanner, on_delete=models.PROTECT, blank=True,
                                  null=True)
    tour_operator = models.ForeignKey(TourOperator,
                                      models.PROTECT,
                                      blank=True,
                                      null=True)
    itinerary = models.ForeignKey(Itinerary,
                                  models.PROTECT,
                                  blank=True,
                                  null=True)
    photo = models.ForeignKey(Photo,
                              models.PROTECT,
                              blank=True,
                              null=True)
    country_indexes = models.ManyToManyField('places.CountryIndex', blank=True)
    image = models.ImageField(upload_to='images/ads/%Y/%m/%d')
    content = models.TextField()
    link = models.CharField(max_length=300)
    date_created = models.DateTimeField(default=timezone.now)
    date_start = models.DateTimeField(auto_now=True)
    date_end = models.DateTimeField(auto_now=True)
    date_modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    date_deleted = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
