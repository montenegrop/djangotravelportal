from core.models import Page
from places.models import CountryIndex, Park
from django.conf import settings
from reviews.models import AbstractReview
from blog.models import Article
from operators.models import TourOperator
from django.db.models import Q
from django import forms
from core.forms import CustomAuthenticationForm



def footer_pages(request):
    list_pages = ["about-us", "privacy-policy", "careers", 'terms-of-use']
    query = Q()
    for page_slug in list_pages:
        query |= Q(slug=page_slug)
    pages = Page.objects.filter(query)
    return {'pages': pages}

def footer_blog(request):
    articles = Article.objects.filter(article_status=Article.STATUS_PUBLISHED).order_by('-date_created')[:3]
    return {'articles': articles}

def footer_reviews(request):
    reviews = AbstractReview.latest_reviews()
    return {'reviews': reviews}


def navbar_operators(request):
    operators = TourOperator.objects.all()
    return {'navbar_operators': operators}


def all_countries(request):
    countries = CountryIndex.objects.all().order_by('name')
    return {
        'all_countries': countries
    }

def footer_countries(request):
    countries = CountryIndex.objects.all().order_by('name')
    return {
        'countries': countries
    }

def footer_parks(self):
    parks_names = ['Amboseli National Park',
             'Bwindi Impenetrable National Park',
             'Etosha National Park',
             'Hluhluwe Umfolozi Game Reserve',
             'Hwange National Park',
             'Kruger National Park',
             'Liwonde National Park',
             'Masai Mara National Reserve',
             'Moremi Game Reserve',
             'Murchison Falls National Park',
             'Ngorongoro Crater Conservation Area',
             'Serengeti National Park',
             'South Luangwa National Park',
             'Volcanoes National Park', ]
    parks = Park.objects.filter(name__in=parks_names).order_by('name')
    return {
        'parks_footer': parks,
    }

def login_form(request):
    form = CustomAuthenticationForm()
    return {
        'auth_form': form
    }

def favs_count(request):
    from users.logic.favs import get_favs_count
    return {
        'favs_count': get_favs_count(request)
    }

def site_constants(request):
    RECAPTCHA_SITE_KEY = settings.RECAPTCHA_SITE_KEY
    GOOGLE_MAPS_API_KEY = settings.GOOGLE_MAPS_API_KEY
    return {
        'RECAPTCHA_SITE_KEY': RECAPTCHA_SITE_KEY,
        'GOOGLE_MAPS_API_KEY': GOOGLE_MAPS_API_KEY
    }
