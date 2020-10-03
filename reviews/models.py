from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

from analytics.utils import get_country_by_ip
from places.models import Park, Activity, Animal, CountryIndex, Country
from django.utils import timezone
from analytics.models import Action
from itertools import chain
from analytics.models import Analytic


class SafariType(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class FieldOptions(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class FieldType(models.Model):
    FIELD_TYPE_CHOICES = (
        ("CHARFIELD", "CharField"),
        ("CHOICE", "Choice"),
    )
    name = models.CharField(max_length=100,
                            choices=FIELD_TYPE_CHOICES,
                            default="CHARFIELD")
    options = models.ManyToManyField(FieldOptions, blank=True)

    def __str__(self):
        return self.name


class DynamicFieldPark(models.Model):
    name = models.CharField(max_length=200)
    field_type = models.ForeignKey(FieldType, on_delete=models.PROTECT)
    parks = models.ManyToManyField(Park, blank=True)

    def __str__(self):
        return self.name


class DynamicFieldParkValue(models.Model):
    dynamic_field = models.ForeignKey(
        DynamicFieldPark, on_delete=models.PROTECT)
    value = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.name


class AbstractReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=300)
    slug = models.CharField(max_length=1000)
    content = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(default=timezone.now)
    date_deleted = models.DateTimeField(blank=True, null=True)
    ip_address = models.CharField(max_length=300)
    country_written = models.ForeignKey(Country, on_delete=models.PROTECT, null=True)
    email_sent = models.BooleanField(default=False)
    pearls_of_wisdom = models.TextField(blank=True, null=True)
    rejection_text = models.TextField(blank=True, null=True)
    days_booked = models.IntegerField(blank=True, null=True)
    
    friend_recommend = models.BooleanField()
    overall_rating = models.IntegerField()
    
    dynamic_field_values = models.ManyToManyField(
        DynamicFieldParkValue, blank=True)
    activities = models.ManyToManyField(Activity, blank=True)
    animals = models.ManyToManyField(Animal, blank=True)
    PENDING = 'PE'
    REJECTED = 'RE'
    ACTIVE = "AC"
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (REJECTED, 'Rejected'),
        (ACTIVE, 'Active'),
    )
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default=PENDING)
    reject_reason = models.CharField(max_length=4000, blank=True, null=True)
    
    #calculated field
    kudu_count = models.IntegerField(default=0)
    views_count = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        abstract = True

    def title_short(self, n=100):
        return (self.title[:n] + '...') if len(self.title) > n else self.title

    def latest_reviews(tail=4):
        reviews_tour = TourOperatorReview.objects.filter(status="AC").order_by(
            '-date_created')[:tail]
        reviews_park = ParkReview.objects.filter(status="AC").order_by('-date_created')[:4]
        reviews = chain(reviews_park, reviews_tour)
        reviews = list(reviews)
        reviews.sort(key=lambda r: r.date_created, reverse=True)
        reviews = reviews[:tail]
        return reviews


class ParkReview(AbstractReview):
    park = models.ForeignKey('places.Park', on_delete=models.PROTECT, related_name='park_reviews')
    quality_wildlife_rating = models.IntegerField()
    quality_lodging_rating = models.IntegerField()
    crowdedness_rating = models.IntegerField()
    book_lodging = models.BooleanField()
    actions = GenericRelation(Action, related_query_name='park_review')
    visit_date = models.DateField()

    def latest_reviews(park=None, tail=4):
        reviews = ParkReview.objects.filter(status="AC")
        if park:
            reviews = reviews.filter(park=park)
        reviews = reviews.order_by('-date_created')[:4]
        reviews = list(reviews)
        reviews.sort(key=lambda r: r.date_created, reverse=True)
        reviews = reviews[:tail]
        return reviews

    def __str__(self):
        return self.park.name

    def update_kudu_count(self):
        self.kudu_count = Action.objects.filter(action_type="K", park_review=self).count()
        self.save()

    def update_views_count(self):
        self.views_count = Analytic.objects.filter(activity_type="VISIT", content_type__model="ParkReview",
                                                   object_id=self.pk).count()
        self.save()
        
    def is_tour_operator_review(self):
        return False
    
    def is_park_review(self):
        return True



class KilimanjaroParkReview(ParkReview):
    reached_summit = models.BooleanField()
    take_medications = models.BooleanField()
    ROUTE_LEMOSHO = 'LE'
    ROUTE_MACHAME = 'MC'
    ROUTE_MARANGU = 'MR'
    ROUTE_NORTHERN_CIRCUIT = 'NC'
    ROUTE_RONGAI = 'RO'
    ROUTE_SHIRA = 'SH'
    ROUTE_UMBWE = 'UM'

    ROUTES_CHOICES = (
        (ROUTE_LEMOSHO, 'Lemosho'),
        (ROUTE_MACHAME, 'Machame'),
        (ROUTE_MARANGU, 'Marangu'),
        (ROUTE_NORTHERN_CIRCUIT, 'Northern Circuit'),
        (ROUTE_RONGAI, 'Rongai'),
        (ROUTE_SHIRA, 'Shira'),
        (ROUTE_UMBWE, 'Umbwe'),
    )
    route_to_climb = models.CharField(blank=True, max_length=40, choices=ROUTES_CHOICES, default=None)
    other_route_to_climb = models.CharField(blank=True, null=True, max_length=40, default=None)

    def update_kudu_count(self):
        self.kudu_count = Action.objects.filter(action_type="K", park_review=self).count()
        self.save()

    def update_views_count(self):
        self.views_count = Analytic.objects.filter(activity_type="VISIT", content_type__model="KilimanjaroParkReview",
                                                   object_id=self.pk).count()
        self.save()

    def __str__(self):
        return self.park.name


class TourOperatorReview(AbstractReview):
    tour_operator = models.ForeignKey(
        'operators.TourOperator', on_delete=models.PROTECT, related_name='tour_operator_reviews')
    safari_type = models.ForeignKey(SafariType, on_delete=models.PROTECT, null=True)
    did_not_go = models.BooleanField()
    #visit date = start_date
    start_date = models.DateField(blank=True,null=True)

    meet_and_greet_rating = models.IntegerField()
    responsiveness_rating = models.IntegerField()
    safari_quality_rating = models.IntegerField()
    itinerary_quality_rating = models.IntegerField()
    overall_rating = models.IntegerField()
    vehicle_rating = models.IntegerField()

    response = models.TextField(null=True)
    response_date = models.DateField(null=True)
    response_email_sent = models.BooleanField(default=False)

    actions = GenericRelation(
        Action, related_query_name='tour_operator_review')
    country_indexes = models.ManyToManyField(CountryIndex, blank=True, related_name='tour_operator_reviews')
    parks = models.ManyToManyField(Park, blank=True)


    reached_summit = models.BooleanField(default=False)
    take_medications = models.BooleanField(default=False)
    route_to_climb = models.CharField(null=True,blank=True, max_length=40,
                                      choices=KilimanjaroParkReview.ROUTES_CHOICES, default=None)
    other_route_to_climb = models.CharField(blank=True, null=True, max_length=40, default=None)

    FRIEND = 'A friend/family recommended them'
    GOOGLE = 'Google search'
    TRADE_SHOW = 'Trade show'
    ARTICLE = 'Article in newspaper/magazine'
    WEBSITE = 'Website'
    FIND_OUT_CHOICES = (
        (FRIEND, 'A friend/family recommended them'),
        (GOOGLE, 'Google search'),
        (TRADE_SHOW, 'Trade show'),
        (ARTICLE, 'Article in newspaper/magazine'),
        (WEBSITE, 'Website'),
    )
    find_out = models.CharField(
        max_length=40, choices=FIND_OUT_CHOICES, blank=True, null=True)
    find_out_website = models.CharField(max_length=600, blank=True, null=True)
    kudu_count = models.IntegerField(default=0)

    def update_views_count(self):
        self.views_count = Analytic.objects.filter(activity_type="VISIT", content_type__model="TourOperatorReview",
                                                   object_id=self.pk).count()
        self.save()
    
    def is_tour_operator_review(self):
        return True
    
    def is_park_review(self):
        return False

    def update_kudu_count(self):
        self.kudu_count = Action.objects.filter(action_type="K", tour_operator_review=self).count()
        self.save()

    def __str__(self):
        return self.tour_operator.name
