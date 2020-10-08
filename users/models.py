from django.db.models.signals import post_save
from django.dispatch import receiver
from operators.models import Itinerary
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from operators.models import TourOperator
from django.template import defaultfilters
from analytics.models import Action
from django.db.models import Q, Sum
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone


class Badge(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name

class Fav(models.Model):
    itinerary = models.ForeignKey(Itinerary,models.PROTECT,related_name='favs',blank=True, null=True)
    tour_operator = models.ForeignKey(TourOperator,models.PROTECT,related_name='favs',blank=True, null=True)
    user = models.ForeignKey(User,models.PROTECT,related_name='favs',blank=True,  null=True)
    uuid = models.CharField(max_length=300,blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    date_deleted = models.DateTimeField(blank=True, null=True)
    

class UserProfile(models.Model):
    GENDER_CHOICES = (
        ("M", "Male"),
        ("F", "Female"),)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    badges = models.ManyToManyField(Badge, blank=True)
    screen_name = models.CharField(null=True, max_length=200)
    gender = models.CharField(max_length=15,
                              choices=GENDER_CHOICES,
                              default="M", null=True)
    country = models.ForeignKey('places.Country', null=True, on_delete=models.PROTECT)
    tour_operator = models.ForeignKey(TourOperator, blank=True, null=True, on_delete=models.PROTECT, related_name='profiles')
    date_of_birth = models.DateField(null=True, blank=True)
    safari_count = models.IntegerField(default=0, null=True, blank=True)
    first_kudu_email = models.BooleanField(default=False, blank=True, null=True)
    description = models.TextField(null=True, blank=True)

    Luxury = "Luxury"
    Mid = "Mid"
    Basics = "Back-to-basics"

    LUXURY_LEVEL_CHOICES = (
        (Luxury,'Luxury'),
         #'Fly me in to a private, tented camp where I can enjoy the finest foods, wines and linens. I’m after exclusive, intimate camps with refined touches.'),
        (Mid, "Mid"),
         #'I tend to stay in the main camps and lodges. It suits my budget and my preference for creature comforts, such as electricity and hot water.'),
        (Basics,"Back-to-basics"),
         #'I prefer old school camping and can pitch a mean tent. I like being off the grid and am ready to sleep under the stars. I don’t mind helping set-up or cook dinner. I’m the original safari enthusiast! '),
    )

    luxury_level = models.CharField(max_length=20, null=True, choices=LUXURY_LEVEL_CHOICES)
    big_five = models.IntegerField(default=0, null=True, blank=True)
    avatar = models.ImageField(upload_to='images/user_avatar/%Y/%m/%d', null=True, blank=True)
    send_newsletter = models.BooleanField(default=False, null=True)
    use_screen_name = models.BooleanField(default=False, null=True, blank=True)
    hide_email = models.BooleanField(default=False, null=True)
    withhold_information = models.BooleanField(default=False, null=True)
    welcome_email_sent = models.BooleanField(default=False)
    suppress_email = models.BooleanField(default=False, blank=True, null=True)
    countries_visited = models.ManyToManyField('places.CountryIndex', blank=True, related_name="countries_visited")
    parks_visited = models.ManyToManyField('places.Park', blank=True, related_name="parks_visited")
    animals_seen = models.ManyToManyField('places.Animal', blank=True)
    activities_enjoy = models.ManyToManyField(
        'places.Activity', blank=True, related_name="activities_enjoy")
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)


    # social media
    website = models.CharField(max_length=1000, blank=True, null=True)
    whatsapp = models.CharField(max_length=1000, blank=True, null=True)
    blog = models.CharField(max_length=1500, blank=True, null=True)
    skype = models.CharField(max_length=1000, blank=True, null=True)
    linkedin = models.CharField(max_length=1000, blank=True, null=True)
    facebook = models.CharField(max_length=1000, blank=True, null=True)
    pinterest = models.CharField(max_length=1000, blank=True, null=True)
    instagram = models.CharField(max_length=1000, blank=True, null=True)
    youtube = models.CharField(max_length=1000, blank=True, null=True)
    twitter = models.CharField(max_length=1000, blank=True, null=True)


    LODGE_OWNER = "LO"
    NON_PROFIT = "NP"
    SAFARI_GUIDE = "SG"
    SAFARI_ENTHUSIAST = "SE"
    SAFARI_TOUR_OPERATOR = "TO"
    TRAVEL = "TA"
    TRAVEL_WRITE = "TW"

    USER_TYPE_CHOICES = (
        (LODGE_OWNER, 'Lodge staff/owner'),
        (NON_PROFIT, 'Non-profit'),
        (SAFARI_GUIDE, 'Safari driver/guide'),
        (SAFARI_ENTHUSIAST, 'Safari enthusiast'),
        (SAFARI_TOUR_OPERATOR, 'Safari tour operator'),
        (TRAVEL, 'Travel agency'),
        (TRAVEL_WRITE, 'Travel writer'),
    )

    user_type = models.CharField(null=True, max_length=5, choices=USER_TYPE_CHOICES)

    #calculated fields
    reviews_count = models.IntegerField(default=0)
    kudus_count = models.IntegerField(default=0)

    def has_social_media(self):
        if self.whatsapp or self.skype or self.linkedin or self.facebook or self.pinterest or self.instagram or self.youtube or self.twitter:
            return True
        else:
            return False

    def has_website_or_blog(self):
        if self.blog or self.website:
            return True
        else:
            return False

    def __str__(self):
        return self.screen_name or self.user.email

    def display_name_slugged(self):
        if self.use_screen_name:
            name = self.screen_name
        else:
            name = self.user.first_name + ' ' + self.user.last_name
        return defaultfilters.slugify(name)

    def is_tour_operator(self):
        return self.user.groups.filter(name="Tour Operator").exists() and self.tour_operator


    def update_review_count(self):
        count = self.user.touroperatorreview_set.filter(status="AC").count() + self.user.parkreview_set.filter(status="AC").count()
        self.reviews_count = count
        self.save()
    
    def update_kudus_count(self):
        self.kudus_count = Action.objects.filter(action_type="K", user=self.user).count()
        self.save()

    def contribution_count(self):
        return self.user.touroperatorreview_set.filter(status="AC").count() + \
               self.user.parkreview_set.filter(status="AC").count() + \
               self.user.article_set.filter(article_status="PUBLISHED").count()

    def display_name(self):
        if self.use_screen_name:
            return self.screen_name
        else:
            return self.user.first_name + " " + self.user.last_name

    def display_name_for_email(self):
        if self.screen_name:
            return self.screen_name
        if self.user.first_name:
            return self.user.first_name
        return ""
        
    def display_name2(self):
        if self.use_screen_name:
            return self.screen_name
        else:
            return self.user.first_name

    def kudu_count(self):
        operator_review_kudus = self.user.touroperatorreview_set.aggregate(Sum("kudu_count"))["kudu_count__sum"] or 0
        park_review_kudus = self.user.parkreview_set.aggregate(Sum("kudu_count"))["kudu_count__sum"] or 0
        article_kudus = self.user.article_set.aggregate(Sum("kudu_count"))["kudu_count__sum"] or 0
        photo_kudus = self.user.photo_set.aggregate(Sum("kudu_count"))["kudu_count__sum"] or 0
        return operator_review_kudus + park_review_kudus + article_kudus + photo_kudus

def set_last_seen(sender, user, request, **kwargs):
    if user.profile.is_tour_operator() and not len(request.session.get("exit_users_pk", default=[])):
        user.profile.tour_operator.last_seen = timezone.now()
        user.profile.tour_operator.save()

user_logged_in.connect(set_last_seen)


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created and not UserProfile.objects.filter(user=instance).exists():
        UserProfile.objects.create(user=instance)
    instance.profile.save()