from django.db import models
from django.db.models import Avg
from django.db.models.functions import Coalesce
from django.contrib.contenttypes.fields import GenericRelation
from django.utils import timezone

from analytics.models import Analytic
from places.models import CountryIndex, Park
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta
from datetime import datetime
from django.db.models import Count, Avg
from django.db.models import Max
from places.models import Country
from django.utils.timezone import make_aware
from django.db.models import Q, OuterRef, Subquery, PositiveIntegerField

class Package(models.Model):
    name = models.CharField(max_length=300)
    show_contact_information = models.BooleanField(default=False)
    show_contact_form = models.BooleanField(default=False)
    show_logo = models.BooleanField(default=False)
    show_gallery = models.BooleanField(default=False)
    show_social_network = models.BooleanField(default=False)
    show_itinerary = models.BooleanField(default=False)
    max_description = models.IntegerField(default=0)
    max_vehicle_description = models.IntegerField(default=0)
    max_photo = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class TourOperator(models.Model):
    LUXURY_LEVEL_BUDGET = 'BUDGET'
    LUXURY_LEVEL_MID_LEVEL = 'MID_LEVEL'
    LUXURY_LEVEL_ULTRA_SAFARI = 'ULTRA_SAFARI'
    LUXURY_LEVEL_CHOICES = (
        (LUXURY_LEVEL_BUDGET, "Budget"),
        (LUXURY_LEVEL_MID_LEVEL, "Mid-range"),
        (LUXURY_LEVEL_ULTRA_SAFARI, "Luxury"),
    )
    luxury_level = models.CharField(max_length=25,
                                    choices=LUXURY_LEVEL_CHOICES,
                                    default=LUXURY_LEVEL_MID_LEVEL)

    name = models.CharField(max_length=300, verbose_name=u"Company name")
    name_short = models.CharField(max_length=300, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=False)
    description = models.TextField(blank=True, null=True)
    vehicle_description = models.TextField(blank=True, null=True)
    projects = models.CharField(max_length=300, blank=True, null=True)
    headquarters = models.ForeignKey('places.Country',
                                     on_delete=models.PROTECT,
                                     blank=True,
                                     null=True)
    package = models.ForeignKey(Package,
                                     on_delete=models.PROTECT,
                                     blank=True,
                                     null=True)
    logo = models.ImageField(upload_to='images/touroperators_logo/%Y/%m/%d', blank=True, null=True)
    startup_date = models.DateField(blank=True, null=True)
    last_seen = models.DateTimeField(blank=True, null=True)
    last_reviewed = models.DateField(blank=True, null=True)
    tailored_safari = models.BooleanField(default=True)
    #user that submits the request
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    book_attraction = models.BooleanField(default=True)
    international_flight = models.BooleanField(default=True)
    group_safari = models.BooleanField(default=True)
    contact = models.CharField(
        max_length=300, blank=True, null=True, verbose_name=u"Contact name")
    email = models.EmailField(blank=True, null=True)
    secondary_email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=300, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    validated = models.BooleanField(default=True)
    country_indexes = models.ManyToManyField(
        'places.CountryIndex', blank=True, related_name='tour_operators')
    languages = models.ManyToManyField('places.Language', blank=True)
    parks = models.ManyToManyField(
        'places.Park', blank=True, related_name='tour_operators')
    date_deleted = models.DateTimeField(blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(auto_now=True)
    first_kudu_email = models.BooleanField(
        default=False, blank=True, null=True)
    not_trading = models.BooleanField(default=False)
    out_of_business = models.BooleanField(default=False)
    yas_modifier = models.IntegerField(default=0)
    suppress_email = models.BooleanField(default=False)
    widget_added = models.BooleanField(default=False)
    draft = models.BooleanField(default=False)
    # social media
    website = models.CharField(max_length=1000, blank=True, null=True)
    whatsapp = models.CharField(max_length=1000, blank=True, null=True)
    blog = models.CharField(max_length=1000, blank=True, null=True)
    skype = models.CharField(max_length=1000, blank=True, null=True)
    linkedin = models.CharField(max_length=1000, blank=True, null=True)
    facebook = models.CharField(max_length=1000, blank=True, null=True)
    pinterest = models.CharField(max_length=1000, blank=True, null=True)
    instagram = models.CharField(max_length=1000, blank=True, null=True)
    youtube = models.CharField(max_length=1000, blank=True, null=True)
    twitter = models.CharField(max_length=1000, blank=True, null=True)
    yas_score = models.IntegerField(default=0)
    #last_visit = models.DateTimeField(null=True, blank=True)

    yas_score_temp_country = 0
    date_modified_yas_score = models.DateTimeField(blank=True, null=True)
    
    # calculated fields
    reviews_count = models.IntegerField(blank=True, null=True)
    average_rating = models.IntegerField(blank=True, null=True)
    packages_count = models.IntegerField(blank=True, null=True)
    photos_count = models.IntegerField(blank=True, null=True)
    quote_request_count = models.IntegerField(blank=True, null=True)
    parks_count = models.IntegerField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    last_review_date = models.DateField(blank=True, null=True)
    
    def update_photos_count(self):
        from photos.models import Photo
        photos = Photo.objects.filter(date_deleted__isnull=True)
        photos = photos.filter(draft=False)
        photos = photos.filter(tour_operator=self)
        photos = photos.filter(image__isnull=False)
        photos = photos.exclude(image__exact='')
        self.photos_count = photos.count() or 0
        self.save()

    def has_owner(self):
        return self.profiles.all().exists()

    def quick_to_respond(self):
        if not self.last_seen:
            return False
        return self.last_seen.date() and datetime.now().date() - timedelta(days=7) <= self.last_seen.date()

    def update_yas_score(self, country_index=None):
        score = 35
        score += self.yas_score_not_trading()
        score += self.yas_score_widget()
        score += self.yas_score_modifier()
        score += self.yas_score_packages()
        score += self.yas_score_vehicle_description()
        score += self.yas_score_company_age()
        score += self.yas_score_social_media()
        score += self.yas_score_photos_age()
        score += self.yas_score_itinerary_age()
        score += self.yas_score_more_information()
        score += self.yas_score_last_3_months()
        score += self.yas_score_parkreviews()
        score += self.yas_score_articles_count()
        score += self.yas_score_itineraries()
        score += self.yas_score_review_responses()
        if country_index:
            self.yas_score_temp_country = country_index
            score += self.yas_score_per_country()
        else:
            score += self.yas_score_number_of_reviews()
            score += self.yas_score_last_review_date()
            score += self.yas_score_average_reviews()
            score += self.yas_score_one_country()

        score = int(score)
        if score > 99:
            score = 99
        if score < 15:
            score = 15
        # save in db
        
        if country_index:
            yas_score, _ = YASScore.objects.get_or_create(tour_operator=self, country_index=country_index)
            yas_score.yas_score = score
            self.date_modified_yas_score = make_aware(datetime.today())
            self.save()
            yas_score.save()
        else:
            #yas_score, _ = YASScore.objects.get_or_create(tour_operator=self, country_index=None)
            #yas_score.yas_score = score
            #yas_score.save()
            self.date_modified_yas_score = make_aware(datetime.today())
            self.yas_score = score
            self.save()
        return score

    def yas_score_not_trading(self):
        return 0 if self.is_active else -35

    def yas_score_widget(self):
        if self.widget_added:
            return 5
        return 0

    def yas_score_modifier(self):
        return self.yas_modifier

    def yas_score_packages(self):
        itineraries = Itinerary.objects.filter(tour_operator=self, date_deleted__isnull=False)
        if itineraries.exists():
            return 1
        return 0

    def yas_score_vehicle_description(self):
        if self.vehicle_description:
            return 1
        return 0

    def yas_score_company_age(self):
        if self.date_created:
            age_delta = now() - self.date_created
            age_days = age_delta.days
            return round(2 * (age_days / (1200 + age_days)))
        return 0

    def yas_score_social_media(self):
        if self.facebook or self.twitter or self.pinterest or self.youtube:
            return 1
        return 0

    def yas_score_photos_age(self):
        if self.photos.count() > 0:
            photo = self.photos.last()
            photo_days = (now() - photo.date_modified).days
            if photo_days < 185:
                return round(4 * ((185 - photo_days) / 185),2)
        return 0

    def yas_score_itinerary_age(self):
        if self.itineraries.count() > 0:
            itinerary = self.itineraries.order_by('-date_modified').first()
            itinerary_days = (now() - itinerary.date_modified).days
            if itinerary_days < 365:
                return round(8 * ((365 - itinerary_days) / 365),2)
        return 0

    def yas_score_more_information(self):
        from django.utils.timezone import make_aware
        six_months = datetime.today() - timedelta(days=180)
        six_months = make_aware(six_months)
        informations = self.quote_requests.filter(date_created__gte=six_months).count()
        if informations > 6:
            return 3
        return round(informations * 0.5,2)

    def yas_score_last_3_months(self):
        if self.last_seen:
            date_format = "%Y-%m-%d"
            now = datetime.strptime(str(datetime.now().date()), date_format)
            last_seen = datetime.strptime(str(self.last_seen.date()), date_format)
            delta = now - last_seen
            if delta.days < 90:
                return round(8 * ((90 - delta.days) / 90),2)
        return 0

    def yas_score_parkreviews(self):
        from reviews.models import ParkReview
        profiles = self.profiles.all()
        users = [profile.user for profile in profiles]
        park_reviews_count = ParkReview.objects.filter(user__in=users).count()
        park_score = 5 * (park_reviews_count / (5 + park_reviews_count))
        return round(park_score,2)


    def yas_score_articles_count(self):
        from blog.models import Article
        profiles = self.profiles.all()
        users = [profile.user for profile in profiles]
        articles_count = Article.objects.filter(user__in=users).count()
        article_score = 3 * (articles_count / (5 + articles_count))
        return round(article_score,2)

    def yas_score_itineraries(self):
        itineraries_count = Itinerary.objects.filter(tour_operator=self, date_deleted__isnull=True).count()
        return round(3 * (itineraries_count / (2 + itineraries_count)),2)

    def yas_score_review_responses(self):
        from reviews.models import TourOperatorReview
        tour_reviews_count = TourOperatorReview.objects.filter(tour_operator=self, status="AC").count()
        tour_reviews_responses_count = TourOperatorReview.objects.filter(tour_operator=self, status="AC",
                                                                         response__isnull=False).count()
        if tour_reviews_count > 0:
            return round(2 * (tour_reviews_responses_count / tour_reviews_count),2)
        return 0

    def yas_score_number_of_reviews(self):
        from reviews.models import TourOperatorReview
        tour_reviews_count = TourOperatorReview.objects.filter(tour_operator=self, status="AC").count()
        return round(10 * (tour_reviews_count / (5 + tour_reviews_count)),2)

    def yas_score_last_review_date(self):
        from reviews.models import TourOperatorReview
        last_review = TourOperatorReview.objects.filter(tour_operator=self, status="AC").order_by(
            '-date_modified').first()
        if last_review:
            last_review_days = (now() - last_review.date_modified).days
            if last_review_days < 185:
                return round(5 * ((185 - last_review_days) / 185),2)
        return 0

    def yas_score_average_reviews(self):
        tour_reviews = self.tour_operator_reviews.all().aggregate(Avg('overall_rating'))
        tour_reviews_avg = tour_reviews['overall_rating__avg']
        if tour_reviews_avg:
            return round(3 * tour_reviews_avg,2)
        return 0
        #

    def yas_score_one_country(self):
        countries_count = self.country_indexes.all().count()
        if countries_count > 5:
            return 1
        if countries_count == 1:
            return -1
        return 0

    def yas_score_per_country_reviews(self):
        reviews_in_country_index = self.tour_operator_reviews.filter(status='AC',country_indexes=self.yas_score_temp_country)
        reviews_in_country_index = reviews_in_country_index.order_by('-date_modified')
        return 10 * (reviews_in_country_index.count() / (5 + reviews_in_country_index.count()))

    def yas_score_per_country_last_review(self):
        reviews_in_country_index = self.tour_operator_reviews.filter(status='AC',country_indexes=self.yas_score_temp_country)
        reviews_in_country_index = reviews_in_country_index.order_by('-date_modified')
        last_review = reviews_in_country_index.first()
        if last_review:
            last_review_days = (now() - last_review.date_modified).days
            if last_review_days < 185:
                return 5 * ((185 - last_review_days) / 185)
        return 0

    def yas_score_per_country_operating_in(self):
        operating_countries_indexes_count = self.country_indexes.all().count()
        if operating_countries_indexes_count == 1:
            return 2
        if operating_countries_indexes_count == 2:
            return 1
        return 0

    def yas_score_per_country_reviews_rating(self):
        reviews_in_country_index = self.tour_operator_reviews.filter(status='AC',country_indexes=self.yas_score_temp_country)
        reviews_in_country_index = reviews_in_country_index.order_by('-date_modified')
        if reviews_in_country_index.count():
            reviews_in_country_index_rating = 0
            for review in reviews_in_country_index:
                reviews_in_country_index_rating += review.overall_rating
            return 3 * (reviews_in_country_index_rating) / reviews_in_country_index.count()
        return 0


    def yas_score_per_country(self):
        score = 0
        score += self.yas_score_per_country_reviews()
        score += self.yas_score_per_country_last_review()
        score += self.yas_score_per_country_operating_in()
        score += self.yas_score_per_country_reviews_rating()
        return score

    def __str__(self):
        return self.name

    def latest_added(tail=4):
        operators = TourOperator.objects.filter(draft=False).filter(date_deleted__isnull=True).order_by(
            '-date_created')[:4]
        return operators

    def email_recipient_list(self):
        if self.suppress_email or self.not_trading or self.out_of_business:
            return []
        else:
            res = []
            if self.email:
                res.append(self.email)
            if self.secondary_email:
                res.append(self.secondary_email)
            for userprofile in self.profiles.all():
                res.append(userprofile.user.email)
            return res

    def update_reviews_count(self):
        self.reviews_count = self.tour_operator_reviews.all().count()
        self.save()

    def update_park_reviews_count(self):
        from reviews.models import ParkReview
        profiles = self.profiles.all()
        users = [profile.user for profile in profiles]
        park_reviews_count = ParkReview.objects.filter(user__in=users).count()
        self.park_reviews_count = park_reviews_count
        self.save()

    def update_quote_request_count(self):
        self.quote_request_count = self.quote_requests.all().count()
        self.save()

    def update_parks_count(self):
        self.parks_count = self.parks.all().count()
        self.save()

    def update_average_rating(self):
        average_rating = self.tour_operator_reviews.filter(overall_rating__isnull=False).aggregate(avg=Avg('overall_rating'))
        self.average_rating = average_rating['avg']
        self.save()

    def update_packages_count(self):
        self.packages_count = self.itineraries.all().count()
        self.save()

    def operator_that_choices():
        return {
        'respond-24h': {
            'title': 'Respond within 24 hours',
            'annotate': None,
            'query': Q(last_seen__gte=timezone.now()-timedelta(hours=24))
        },
        'focus-one': {
            'title': 'Focus on only one country',
            'annotate': Count('country_indexes'),
            'query': Q(subquery_alias = 1)
        },
        'offer-custom': {
            'title': 'Offer custom safaris',
            'annotate': None,
            'query': Q(tailored_safari = True)
        },
        'offer-group': {
            'title': 'Offer group safaris',
            'annotate': None,
            'query': Q(group_safari = True)
        },
        'has-itinerary': {
            'title': 'List tours on YAS',
            'annotate': Subquery(
                queryset = Itinerary.objects.filter(
                    tour_operator_id=OuterRef(name='pk')
                ).order_by()
                .values('tour_operator_id')
                .annotate(count=Count('id'))
                .values('count'), output_field = PositiveIntegerField()),
            'query': Q(subquery_alias__gte = 1)
        },
        'inter-flight': {
            'title': 'Book intl. flights',
            'annotate': None,
            'query': Q(international_flight = True)
        },
        'pre-post-actvities': {
            'title': 'Book pre-/post-safari actvities',
            'annotate': None,
            'query': Q(book_attraction = True)
        },
    }

    
    def is_fav(self, request):
        from users.models import Fav
        if not request.user.is_authenticated and not 'uuid' in request.session:
            return False
        if request.user.is_authenticated:
            fav = Fav.objects.filter(user = request.user, tour_operator=self, date_deleted__isnull=True).first()
            return fav != None
        if 'uuid' in request.session:
            session_uuid = request.session['uuid']
            fav = Fav.objects.filter(uuid = session_uuid, tour_operator=self, date_deleted__isnull=True).first()
            return fav != None

class YASScore(models.Model):
    tour_operator = models.ForeignKey(TourOperator, models.PROTECT, related_name='score')
    country_index = models.ForeignKey(CountryIndex, models.PROTECT, null=True, related_name='score')
    yas_score = models.IntegerField(default=0)
    date_modified = models.DateTimeField(auto_now=True)

class Month(models.Model):
    name = models.CharField(max_length=300)
    name_short = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class ItineraryType(models.Model):
    name = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Itinerary types"

class ItineraryFocusType(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class ItineraryInclusion(models.Model):
    name = models.CharField(max_length=300)
    explanation = models.CharField(max_length=400, blank=True, null=True)
    date_modified = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ItineraryExclusion(models.Model):
    name = models.CharField(max_length=300)
    explanation = models.CharField(max_length=400, blank=True, null=True)
    date_modified = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Itinerary(models.Model):
    itinerary_type = models.ForeignKey(ItineraryType, models.PROTECT)
    image = models.ImageField(upload_to='images/itineraries/%Y/%m/%d')
    safari_focus_activity = models.ForeignKey('places.Activity', models.PROTECT, related_name='safaris', null=True)
    non_safari_focus_activity = models.ForeignKey('places.Activity', models.PROTECT, related_name='nonsafaris', null=True, blank=True)
    secondary_focus_activity = models.ManyToManyField('places.Activity', related_name='secondaries', blank=True)
    title = models.CharField(max_length=300)
    title_short = models.CharField(max_length=300, blank=True, null=True)
    slug = models.SlugField(max_length=255)
    tour_operator = models.ForeignKey(
        TourOperator, models.PROTECT, related_name='itineraries')
    header = models.TextField(blank=True, null=True)
    needs_update = models.BooleanField(default=True)
    summary = models.TextField(blank=True, null=True)
    content = models.TextField()
    accomodation = models.TextField(blank=True, null=True)
    currency = models.ForeignKey('places.Currency',
                                 on_delete=models.PROTECT,
                                 blank=True,
                                 null=True)
    # user input
    min_price = models.DecimalField(max_digits=10,
                                    decimal_places=2,
                                    blank=True,
                                    null=True)
    # user input
    max_price = models.DecimalField(max_digits=10,
                                    decimal_places=2,
                                    blank=True,
                                    null=True)
    # price in USD
    search_price = models.DecimalField(max_digits=10,
                                       decimal_places=2,
                                       blank=True,
                                       null=True)
    single_supplement = models.BooleanField(default=False)
    accept_terms = models.BooleanField(default=False)
    # user input
    single_supplement_price = models.DecimalField(max_digits=10,
                                                  decimal_places=2,
                                                  blank=True,
                                                  null=True)
    duration = models.CharField(max_length=300, blank=True, null=True)
    days = models.IntegerField(blank=True, null=True, choices=[(i, i) for i in range(19)])

    date_created = models.DateTimeField(default=timezone.now)
    flight = models.BooleanField(default=False)
    date_modified = models.DateTimeField(auto_now=True)
    date_deleted = models.DateTimeField(blank=True, null=True)
    #activities = models.ManyToManyField('places.Activity', blank=True)
    #we shouldn't use this animals field
    animals = models.ManyToManyField('places.Animal', blank=True)
    months = models.ManyToManyField(Month)
    country_indexes = models.ManyToManyField('places.CountryIndex', blank=True, related_name='itineraries')
    parks = models.ManyToManyField('places.Park', blank=True, related_name='itineraries')
    inclusions = models.ManyToManyField(ItineraryInclusion, blank=True, related_name='itineraries_inclusions')
    other_inclusion = models.BooleanField(default=False)
    other_inclusion_text = models.CharField(max_length=300,blank=True,null=True)
    
    exclusions = models.ManyToManyField(ItineraryExclusion, blank=True, related_name='itineraries_exclusions')
    other_exclusion = models.BooleanField(default=False)
    other_exclusion_text = models.CharField(max_length=300,blank=True,null=True)
    activity_level = models.IntegerField(default=0)
    activity_level_name = models.CharField(max_length=300,blank=True,null=True,default='')
    is_featured = models.BooleanField(default=False)
    class Meta:
        verbose_name_plural = "Itineraries"        

    def calc_max_activity_level(self):
        #average of all realted activities
        main_focus_al, non_safari_focus_al, secondary_focus_al = 0, 0, 0
        if self.safari_focus_activity:
            main_focus_al = self.safari_focus_activity.activity_level
        if self.non_safari_focus_activity:
            non_safari_focus_al = self.non_safari_focus_activity.activity_level
        if self.secondary_focus_activity.exists():
            secondary_focus_al = self.secondary_focus_activity.all().aggregate(Max('activity_level'))['activity_level__max']
        max_level = max(main_focus_al, secondary_focus_al,non_safari_focus_al)
        return max_level

    def calc_activity_level_string(self):
        max_level = self.calc_max_activity_level()
        if max_level <= 2.5:
            res = "Easy"
        if max_level <= 4:
            res = "Moderate"
        res = "Strenuous"
        return res
        
    def focus_activities(self, top=3):
        activities = []
        if self.safari_focus_activity:
            activities += [self.safari_focus_activity] 
        if self.non_safari_focus_activity:
            activities += [self.non_safari_focus_activity]
        if self.secondary_focus_activity.exists():
            activities += list(self.secondary_focus_activity.all())
        if len(activities) > 0:
            act_str = []
            for a in activities:
                act_str.append(a.name_short)
            return ', '.join(act_str[:top])
        return False

    def parks_str(self, top=3):
        return ' | '.join(self.parks.all()[:top].values_list('name_short',flat=True))

    def __str__(self):
        return self.title
        
    def price_str(self):
        if self.max_price and self.min_price:
            return "{}-{} {}".format(round(self.min_price), round(self.max_price), self.currency,)
        if self.max_price:
            return round(self.max_price)
        if self.min_price:
            return round(self.min_price)
        return ''

    def price_display(self):
        if self.max_price and self.min_price:
            return "{}-{} {}".format(round(self.min_price), round(self.max_price), self.currency.symbol)
        if self.min_price:
            return "{} {}".format(round(self.min_price), self.currency.symbol)
        return ''
            
    def has_price(self):
        return self.max_price or self.min_price
    
    #calculated field
    visit_count = models.IntegerField(default=0)
    def update_visit_count(self):
        self.visit_count = Analytic.objects.filter(
            activity_type="VISIT", content_type__model="itinerary", object_id=self.id).count()
        self.save()

    def is_fav(self, request):
        from users.models import Fav
        if not request.user.is_authenticated and not 'uuid' in request.session:
            return False
        if request.user.is_authenticated:
            fav = Fav.objects.filter(user = request.user, itinerary=self, date_deleted__isnull=True).first()
            return fav != None
        if 'uuid' in request.session:
            session_uuid = request.session['uuid']
            fav = Fav.objects.filter(uuid = session_uuid, itinerary=self, date_deleted__isnull=True).first()
            return fav != None



class ItineraryDayDescription(models.Model):
    itinerary = models.ForeignKey(Itinerary, models.CASCADE, related_name='day_descriptions')
    day_number = models.IntegerField()
    title = models.CharField(max_length=300)
    description = models.CharField(max_length=5000)
    lodging = models.CharField(max_length=300, blank=True, null=True)
    parks = models.ManyToManyField(Park, blank=True)
    date_deleted = models.DateTimeField(blank=True, null=True)


class QuoteRequest(models.Model):
    tour_operator = models.ForeignKey(TourOperator, models.PROTECT, related_name='quote_requests', blank=True, null=True)
    itinerary = models.ForeignKey(Itinerary, models.PROTECT, related_name='quote_requests', blank=True, null=True)
    
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    name = models.CharField(max_length=600)
    email = models.EmailField()
    country = models.ForeignKey('places.Country', null=True, blank=True, on_delete=models.PROTECT)
    
    date_trip = models.DateField()
    days = models.IntegerField()

    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(blank=True, null=True)
    date_deleted = models.DateTimeField(blank=True, null=True)
    
    telephone = models.CharField(max_length=300, blank=True, null=True)
    party_size = models.CharField(max_length=300)
    
    additional_information = models.TextField()
    
    follow_up_email_sent = models.BooleanField(default=False)
    ip_address = models.CharField(max_length=300, blank=True, null=True)
    STATUS_PENDING = 'PENDING'
    STATUS_QA = 'QA'
    STATUS_CHOICES = (
        (STATUS_QA, "QA"),
        (STATUS_PENDING, "Pending"),
        ("SEEN", "Seen"),
    )
    status = models.CharField(max_length=15,
                              choices=STATUS_CHOICES,
                              default=STATUS_QA)
    seen = models.BooleanField(default=False)
    seen_on = models.DateTimeField(blank=True, null=True)
    itinerary_type = models.ForeignKey(
        ItineraryType, models.PROTECT, blank=True, null=True)
    country_indexes = models.ManyToManyField(CountryIndex, blank=True)
