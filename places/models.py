from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
import textwrap
from django.utils.html import strip_tags
from django.db.models import Avg
from django.db.models.functions import Coalesce


class Plug(models.Model):
    name = models.CharField(max_length=300)
    image = models.ImageField(upload_to='images/plugs')

    def __str__(self):
        return self.name


class Vaccination(models.Model):
    name = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Continent(models.Model):
    name = models.CharField(max_length=300)
    name_short = models.CharField(max_length=5)

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=300)
    main = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class AnimalClass(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Currency(models.Model):
    code = models.CharField(max_length=5, null=True)
    symbol = models.CharField(max_length=1, null=True)
    usd_exchange_rate = models.DecimalField(
        max_digits=20, decimal_places=6, null=True)
    date_modified = models.DateTimeField()

    class Meta:
        verbose_name_plural = "currencies"

    def __str__(self):
        return self.code


class Country(models.Model):
    name = models.CharField(max_length=300)
    name_short = models.CharField(max_length=300)
    iso = models.CharField(max_length=45, blank=True, null=True)
    iso3 = models.CharField(max_length=45, blank=True, null=True)
    fips = models.CharField(max_length=45, blank=True, null=True)
    continent = models.ForeignKey(
        Continent, on_delete=models.PROTECT, null=True)
    currency_name = models.CharField(max_length=45, blank=True, null=True)
    currency_code = models.CharField(max_length=45, blank=True, null=True)
    geonameid = models.CharField(max_length=45, blank=True, null=True)
    phone_prefix = models.CharField(max_length=45, blank=True, null=True)
    postal_code = models.CharField(max_length=45, blank=True, null=True)
    languages = models.CharField(max_length=300)
    flag = models.ImageField(upload_to='images/country_flags', null=True)
    flag_flat = models.ImageField(
        upload_to='images/country_flags_flat', null=True)

    class Meta:
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name


class Animal(models.Model):
    name = models.CharField(max_length=300)
    latin_name = models.CharField(max_length=400, blank=True, null=True)
    header_class = models.CharField(max_length=400, blank=True, null=True, default='hero-position-center')
    international_day = models.DateField(blank=True, null=True)
    plural_name = models.CharField(max_length=300)
    name_short = models.CharField(max_length=300, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True)
    animal_class = models.ForeignKey(AnimalClass, on_delete=models.PROTECT)
    sub_heading = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    highlights = models.TextField(blank=True, null=True)
    link = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='images/animals')
    image_mini = models.ImageField(
        upload_to='images/animals_mini', blank=True, null=True)
    image_header = models.ImageField(
        upload_to='images/animals_header', blank=True, null=True)
    header_caption = models.CharField(max_length=300, blank=True, null=True)
    header_link = models.CharField(max_length=800, blank=True, null=True)
    header_alt = models.CharField(max_length=300, blank=True)
    priority = models.IntegerField(blank=True, null=True)
    meta_title = models.CharField(max_length=700, blank=True, null=True)
    meta_keywords = models.CharField(max_length=700, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    country_indexes = models.ManyToManyField('CountryIndex', blank=True)
    parks = models.ManyToManyField('Park', blank=True)

    def mini_description(self, width=100):
        short_text = textwrap.shorten(
            text=strip_tags(self.description), width=width)

        return short_text

    def __str__(self):
        return self.name

    def get_cased_name(self):
        words = self.name.split(' ')
        words_fixed = []
        nouns = ['African', 'Nile']
        for word in words:
            if word in nouns:
                words_fixed.append(word)
            else:
                words_fixed.append(word.lower())
        return ' '.join(words_fixed)

    def get_international_day(self):
        if self.international_day:
            return self.international_day.strftime("%d %B")
        return False


class Activity(models.Model):
    name = models.CharField(max_length=700)
    name_short = models.CharField(max_length=300, blank=True, null=True)
    name_old = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    ACTIVITY_TYPE_CHOICES = (
        ("SAFARI", "Safari"),
        ("NON_SAFARI", "Non-safari"))
    activity_type = models.CharField(max_length=15,
                                     choices=ACTIVITY_TYPE_CHOICES,
                                     default="SAFARI")
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='images/activities',blank=True, null=True)
    priority = models.IntegerField(blank=True, null=True)
    meta_title = models.CharField(max_length=700, blank=True, null=True)
    meta_keywords = models.CharField(max_length=700, blank=True, null=True)
    meta_description = models.CharField(max_length=1500, blank=True, null=True)
    activity_level = models.IntegerField()
    focus_type = models.ManyToManyField('operators.ItineraryFocusType', blank=True, related_name='activities')
    date_modified = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "activities"

    def save(self, *args, **kwargs):
        # this will take care of the saving
        super(Activity, self).save(*args, **kwargs)
        for itinerary in self.safaris.all():
            itinerary.save()
        for itinerary in self.nonsafaris.all():
            itinerary.save()
        for itinerary in self.secondaries.all():
            itinerary.save()

class Park(models.Model):
    name = models.CharField(max_length=300)
    name_short = models.CharField(max_length=300, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True)
    image = models.ImageField(upload_to='images/parks/%Y/%m/%d')
    image_mini = models.ImageField(upload_to='images/parks_mini/%Y/%m/%d', blank=True, null=True)
    header_class = models.CharField(max_length=400, blank=True)
    image_caption = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    getting_there = models.TextField(blank=True, null=True)
    safari_suitability = models.IntegerField(blank=True, null=True)
    header_caption_link = models.CharField(max_length=1500, blank=True, null=True)
    header_alt = models.CharField(max_length=300, blank=True)
    safari_suitability_text = models.CharField(
        max_length=500, blank=True, null=True)
    highlights = models.TextField(blank=True, null=True)
    ANTI_MALARIA_CHOICES = (
        ("NOT_REQUIRED", "Not required"),
        ("RECOMMENDED", "Recommended"),
        ("ABSOLUTELY", "Absolutely!"),)
    anti_malaria = models.CharField(max_length=15,
                                    choices=ANTI_MALARIA_CHOICES,
                                    default="NOT_REQUIRED")
    total_area = models.CharField(max_length=150, blank=True, null=True)
    year_established = models.IntegerField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    activities = models.ManyToManyField(Activity, blank=True)
    meta_title = models.CharField(max_length=700, blank=True, null=True)
    meta_keywords = models.CharField(max_length=700, blank=True, null=True)
    meta_description = models.CharField(max_length=1500, blank=True, null=True)
    is_top = models.BooleanField(default=False)
    safari_focus_activity = models.ForeignKey('places.Activity', models.PROTECT, related_name='parks', null=True)
    secondary_focus_activity = models.ManyToManyField('places.Activity', related_name='parks_secondaries', blank=True)


    
    def rating_decimal(self):
        average_rating = self.park_reviews.filter(status="AC").aggregate(Avg('overall_rating'))
        if average_rating['overall_rating__avg'] is None:
            return 0
        else:
            return "%.2f" % average_rating['overall_rating__avg']

    def rating_float(self):
        average_rating = self.park_reviews.filter(status="AC").aggregate(Avg('overall_rating'))
        if average_rating['overall_rating__avg'] is None:
            return 0
        else:
            return average_rating['overall_rating__avg']

    def __str__(self):
        return self.name

    def country_ids(self):
        idlist = list(self.country_indexes.values_list('id', flat=True))
        idlist = [str(i) for i in idlist]
        return "','".join(idlist)

    class Meta:
        ordering = ['name', ]

    # calculated fields
    reviews_count = models.IntegerField(blank=True, null=True)
    average_rating = models.FloatField(blank=True, null=True)
    packages_count = models.IntegerField(blank=True, null=True)
    photos_count = models.IntegerField(blank=True, null=True)
    tour_operators_count = models.IntegerField(blank=True, null=True)

    def update_tour_operators_count(self):
        self.tour_operators_count = self.tour_operators.all().count() or 0
        self.save()

    def update_reviews_count(self):
        self.reviews_count = self.park_reviews.all().count() or 0
        self.save()

    def update_average_rating(self):
        average_rating = self.park_reviews.all().aggregate(avg=Coalesce(Avg('overall_rating'), 0))
        self.average_rating = average_rating['avg'] or 0
        self.save()

    def update_packages_count(self):
        self.packages_count = self.itineraries.all().count() or 0
        self.save()

    def update_photos_count(self):
        self.photos_count = self.photos.filter(date_deleted__isnull=True).count() or 0
        self.save()


class CountryIndex(models.Model):
    name = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    name_short = models.CharField(max_length=300)
    flag = models.ImageField(upload_to='images/country_index_flags')
    flag_flat = models.ImageField(upload_to='images/country_index_flags_flat')
    image = models.ImageField(upload_to='images/country_index')
    image_header = models.ImageField(upload_to='images/country_index_header')
    image_large = models.ImageField(upload_to='images/country_index_large')
    header_caption = models.CharField(max_length=500)
    header_caption_link = models.CharField(max_length=500, blank=True, null=True)
    header_alt = models.CharField(max_length=300, blank=True)
    header_class = models.CharField(max_length=400, blank=True)
    large_caption = models.CharField(max_length=500)
    airports = models.CharField(max_length=500)
    summary = models.CharField(max_length=500)
    one_line_summary = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    getting_there = models.TextField(blank=True, null=True)
    highlights = models.CharField(max_length=1500, blank=True, null=True)
    capital = models.CharField(max_length=300, blank=True, null=True)
    currency_code = models.CharField(max_length=10, blank=True, null=True)
    currency_name = models.CharField(max_length=100, blank=True, default='')
    currency_amount = models.CharField(max_length=100, blank=True, default='')
    population = models.CharField(max_length=50, blank=True, null=True)
    total_area = models.CharField(max_length=50, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    activities = models.ManyToManyField(Activity, blank=True)
    languages = models.ManyToManyField(Language, blank=True)
    parks = models.ManyToManyField(Park, blank=True, related_name="country_indexes")
    plugs = models.ManyToManyField(Plug, blank=True)
    vaccinations = models.ManyToManyField(Vaccination, blank=True)
    meta_title = models.CharField(max_length=700, blank=True, null=True)
    meta_keywords = models.CharField(max_length=700, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)

    is_top = models.BooleanField(default=False)

    def __str__(self):
        return self.name_short

    class Meta:
        verbose_name_plural = "African countries"

    # calculated fields
    packages_count = models.IntegerField(blank=True, null=True)
    photos_count = models.IntegerField(blank=True, null=True)
    parks_count = models.IntegerField(blank=True, null=True)
    operators_count = models.IntegerField(blank=True, null=True)

    def update_packages_count(self):
        self.packages_count = self.itineraries.all().count()
        self.save()

    def update_operators_count(self):
        self.operators_count = self.tour_operators.all().count()
        self.save()

    def update_parks_count(self):
        self.parks_count = self.parks.all().count()
        self.save()

    def update_photos_count(self):
        self.photos_count = self.photos.all().count()
        self.save()


class Airport(models.Model):
    name = models.CharField(max_length=300)
    country_index = models.ForeignKey(CountryIndex, models.PROTECT)

    def __str__(self):
        return self.name


class Airline(models.Model):
    name = models.CharField(max_length=300, blank=True, null=True)
    website = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    headquarters = models.ForeignKey('places.Country', models.PROTECT)
    image = models.ImageField(upload_to='images/airlines')
    country_indexes = models.ManyToManyField(CountryIndex, blank=True, related_name="airlines")
    parks = models.ManyToManyField(Park, blank=True)

    def __str__(self):
        return self.name
