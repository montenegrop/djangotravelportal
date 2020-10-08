from places.models import Animal, CountryIndex, Park
from django.urls import reverse
from django.template.defaultfilters import register
from math import floor, ceil
from operators.models import TourOperator, Itinerary
from places.models import CountryIndex, Park, Animal
from photos.models import Photo
from reviews.models import TourOperatorReview, ParkReview
from django.contrib.auth.models import User
import re
from easy_thumbnails.templatetags.thumbnail import thumbnail_url
from django.conf import settings
from easy_thumbnails.files import get_thumbnailer
import logging
import datetime
from num2words import num2words
from django import template
import os
from core.models import MediaFile
import datetime
import calendar

from datetime import timedelta, date

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year,month)[1])
    return datetime.date(year, month, day)



@register.filter
def media_full_url(url):
    return settings.BASE_URL + url


@register.filter
def external_url(url):
    if url[:4] == 'http':
        return url
    else:
        return 'http://{}'.format(url)


@register.filter(is_safe=True)
def get_media_img(args):
    slug, alias = args.split(',')
    try:
        media_file = MediaFile.objects.get(slug=slug)
    except MediaFile.DoesNotExist:
        return ""
    thumbnailer = get_thumbnailer(media_file.image).get_thumbnail(settings.THUMBNAIL_ALIASES[''][alias])
    return "<img src='{}' alt='{}'>".format(thumbnailer.url, media_file.alt_text)

@register.filter(name='template_num2words')
def template_num2words(num):
    return num2words(num)


@register.filter(name='queryset_checked')
def queryset_checked(queryset, obj):
    if obj in queryset:
        return "checked='checked'"


@register.filter(name='yes_no')
def yes_no(boole):
    if boole:
        return "yes"
    return "no"


@register.filter(name='dict_key')
def dict_key(d, k):
    '''Returns the given key from a dictionary.'''
    if k in d:
        return d[k]
    return False


@register.filter
def file_exists(file_):
    if file_.storage.exists(file_.name):
        return file_.url
    return False


@register.filter
def get_type(value):
    return type(value)


def get_thumbnailer_(source, alias):
    """
    to be used in .py
    returns a thumbnail
    """
    try:
        source.url
    except ValueError:
        return ""
    thumbnailer = get_thumbnailer(source).get_thumbnail(
        settings.THUMBNAIL_ALIASES[''][alias])
    return thumbnailer.url


@register.filter
def remote_photo(source):
    if settings.REMOTE_PHOTOS:
        return settings.MEDIA_URL + source.url
    return source.url


@register.filter
def hash(h, key):
    if not key in h:
        return None
    return h[key]


@register.filter
def growl_tags(message_tags):
    if 'success' in message_tags:
        return 'success'
    if 'error' in message_tags:
        return 'danger'


@register.filter
def checked(message_tags):
    if 'success' in message_tags:
        return 'success'
    if 'error' in message_tags:
        return 'danger'


@register.filter
def star_rating(value):
    if value == 0:
        ret = '<span class="yellow font-h5" title="{0:.2f} / 5.00">'.format(value)
        for i in '12345':
            ret += '<i class="far fa-star"></i>'
        ret += '</span>'
        return ret
    if not value:
        return ""
    ret = '<span class="yellow font-h5" title="{0:.2f} / 5.00">'.format(value)
    for i in range(floor(value)):
        ret += '<i class="fas fa-star"></i>'
    remaining = 5 % value
    # decimal part
    rest = value - int(value)
    if rest >= 0.25:
        ret += '<i class="fas fa-star-half-alt"></i>'
        remaining = 5 % floor(value + 1)
    else:
        remaining = 5 - floor(value)
    # rest of the values
    for i in range(remaining):
        ret += '<i class="far fa-star"></i>'
    ret += '</span>'
    return ret


@register.filter
def thumbnail_url_(source, alias):
    alias_data = settings.THUMBNAIL_ALIASES[''][alias]
    height = alias_data['size'][0]
    width = alias_data['size'][1]
    try:
        from django.core.files.storage import default_storage
        if source and hasattr(source, 'path') and default_storage.exists(source.path):
            return thumbnail_url(source, alias)
        else:
            return "https://via.placeholder.com/{}x{}".format(height, width)
    except ValueError:
        return "https://via.placeholder.com/{}x{}".format(height, width)



@register.filter
def thumbnail_missing(image, alias = False):
    if alias:
        alias_data = settings.THUMBNAIL_ALIASES[''][alias]
        height = alias_data['size'][0]
        width = alias_data['size'][1]
    try:
        from django.core.files.storage import default_storage
        if image and hasattr(image, 'path') and default_storage.exists(image.path):
            if alias:
                return thumbnail_url(image.url, alias)
            return image.url
        else:
            if alias:
                return "https://via.placeholder.com/{}x{}".format(height, width)
            return "https://via.placeholder.com/150x150"
    except ValueError:
        if alias:
            return "https://via.placeholder.com/{}x{}".format(height, width)
    return "https://via.placeholder.com/150x150"

@register.filter
def image_(image):
    try:
        from django.core.files.storage import default_storage
        if default_storage.exists(image.path):
            return image.url
        else:
            return "https://via.placeholder.com/150"
    except ValueError:
        return "https://via.placeholder.com/150"

@register.filter
def height(source):
    if settings.REMOTE_PHOTOS:
        return 0
    if os.path.exists(source.url):
        return source.height
    return 0


@register.filter
def width(source):
    if settings.REMOTE_PHOTOS:
        return 0
    if os.path.exists(source.url):
        return source.height
    return 0


@register.filter('get_value_from_dict')
def get_value_from_dict(dict_data, key):
    """
    usage example {{ your_dict|get_value_from_dict:your_key }}
    """
    if key:
        return dict_data.get(key)


def get_tour_operators_count():
    return TourOperator.objects.count()


def get_wildlife_count():
    return Animal.objects.count()


def get_tour_packages_count():
    return Itinerary.objects.count()


def get_reviews_count():
    return TourOperatorReview.objects.count() + ParkReview.objects.count()


def get_parks_count():
    return Park.objects.count()


def get_users_count():
    return User.objects.count()


def get_photos_count():
    return Photo.objects.count()


def get_countries_count():
    return CountryIndex.objects.count()


def parse_variable(variable):
    value = False
    if variable == 'countryindex_count':
        value = CountryIndex.objects.count()
    if variable == 'park_count':
        value = Park.objects.count()
    if variable == 'touroperator_count':
        value = TourOperator.objects.filter(date_deleted__isnull=True).count()
    if variable == 'itinerary_count':
        value = Itinerary.objects.filter(date_deleted__isnull=True).count()
    if variable == 'current_year':
        now = datetime.datetime.now()
        value = now.year
    if not value:
        logger = logging.getLogger('django')
        logger.error("No value defined for variable %s" % variable)
        value = "{{%s}}" % variable
    return str(value)


def parse_variables(text):
    words = re.findall(r"\{{(\w+)\}}", text)
    for word in words:
        text = text.replace('{{%s}}' % word, parse_variable(word))
    return text


def auto_link(text, **args):
    if not 'animals' in args:
        args['animals'] = Animal.objects.all()
    if not 'countries' in args:
        args['countries'] = CountryIndex.objects.all()
    if not 'parks' in args:
        args['parks'] = Park.objects.all()
    for country in args['countries']:
        link = "<a href='%s' target='_blank'>%s</a>"
        link = link % (
            reverse('country_index', kwargs={'slug': country.slug}), country.name)
        text = text.replace(country.name, link)
    return text
    for animal in args['animals']:
        if animal.name and animal.name in text:
            link = "<a href='%s' target='_blank'>%s</a>"
            link = link % (
                reverse('animal', kwargs={'slug': animal.slug}), animal.name)
            search = re.compile(r'\b(%s)\b' % animal.name, re.I)
            text = search.sub(link, text)

        if animal.plural_name and animal.plural_name in text:
            link = "<a href='%s' target='_blank'>%s</a>"
            link = link % (
                reverse('animal', kwargs={'slug': animal.slug}), animal.plural_name)
            search = re.compile(r'\b(%s)\b' % animal.plural_name, re.I)
            text = search.sub(link, text)
    return text


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def formatted_decimal_plain(number):
    if number == '':
        return 0
    number = number.replace('$', '').replace(',', '')
    return float(number)
