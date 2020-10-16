from django.shortcuts import render
from django.views.generic.base import TemplateView
import urllib.parse
from django.db.models import Q
from operators.models import TourOperator, Itinerary
from blog.models import Article
from places.models import CountryIndex, Park
from photos.models import Photo
from reviews.models import TourOperatorReview, ParkReview, KilimanjaroParkReview, AbstractReview
from itertools import chain
from django.db.models import Count, Avg
from django.db.models.functions import Coalesce
from search.models import SearchLog
from analytics.utils import get_visitor_data
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def search_tour_operators(query):
    #tour operators
    any_name = Q()
    for bit in query.split():
        any_name &= (
            Q(name__lower__icontains=bit.lower()) |
            Q(name_short__lower__icontains=bit.lower())
        )

    tour_operators = TourOperator.objects.filter(any_name)
    return tour_operators

def search_tour_packages(query):
    any_name = Q()
    for bit in query.split():
        any_name &= (
            Q(title__lower__icontains=bit.lower()) |
            Q(title_short__lower__icontains=bit.lower())
        )
    itineraries = Itinerary.objects.filter(any_name)
    return itineraries

def search_articles(query):
    any_name = Q()
    for bit in query.split():
        any_name &= (
            Q(title__lower__icontains=bit.lower()) |
            Q(title_short__lower__icontains=bit.lower())
        )
    articles = Article.objects.filter(any_name)
    return articles

def search_photos(query):
    any_name = Q()
    for bit in query.split():
        any_name &= (
            Q(caption__lower__icontains=bit.lower())
        )
    photos = Photo.objects.filter(any_name)
    return photos

def search_reviews(query):
    #park reviews
    any_name = Q()
    for bit in query.split():
        any_name &= (
            Q(title__lower__icontains=bit.lower())
        )
    park_reviews = ParkReview.objects.filter(any_name)

    #tour op reviews
    any_name = Q()
    for bit in query.split():
        any_name &= (
            Q(title__lower__icontains=bit.lower())
        )
    tour_op_reviews = TourOperatorReview.objects.filter(any_name)

    #kili reviews
    any_name = Q()
    for bit in query.split():
        any_name &= (
            Q(title__lower__icontains=bit.lower())
        )
    kilimanjaro_reviews = KilimanjaroParkReview.objects.filter(any_name)

    #merge reviews
    reviews = chain(park_reviews, tour_op_reviews, kilimanjaro_reviews)
    reviews = list(reviews)
    reviews.sort(key=lambda r: r.date_created, reverse=True)
    return reviews


class SearchTourOperatorsView(TemplateView):
    template_name = "search/operators.html"
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_reviews'] = AbstractReview.latest_reviews()
        
        query = kwargs.get('query')
        query = urllib.parse.unquote(query)
        query = urllib.parse.unquote_plus(query)
        context['query'] = query
        tour_operators = search_tour_operators(query)
        context['tour_operators_count'] = tour_operators.count()

        page = self.request.GET.get('page', 1)
        paginator = Paginator(tour_operators, 10)
        try:
            context['paginator'] = paginator.page(page)
        except PageNotAnInteger:
            context['paginator'] = paginator.page(1)
        except EmptyPage:
            context['paginator'] = paginator.page(paginator.num_pages)
        
        return context

class SearchTourPackagesView(TemplateView):
    template_name = "search/packages.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_reviews'] = AbstractReview.latest_reviews()
        
        query = kwargs.get('query')
        query = urllib.parse.unquote(query)
        query = urllib.parse.unquote_plus(query)
        context['query'] = query
        packages = search_tour_packages(query)
        context['packages_count'] = packages.count()

        page = self.request.GET.get('page', 1)
        paginator = Paginator(packages, 10)
        try:
            context['paginator'] = paginator.page(page)
        except PageNotAnInteger:
            context['paginator'] = paginator.page(1)
        except EmptyPage:
            context['paginator'] = paginator.page(paginator.num_pages)
        
        return context
    

class SearchBlogView(TemplateView):
    template_name = "search/blog.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_reviews'] = AbstractReview.latest_reviews()
        
        query = kwargs.get('query')
        query = urllib.parse.unquote(query)
        query = urllib.parse.unquote_plus(query)
        context['query'] = query

        articles = search_articles(query)

        context['articles_count'] = articles.count()

        page = self.request.GET.get('page', 1)
        paginator = Paginator(articles, 10)
        try:
            context['paginator'] = paginator.page(page)
        except PageNotAnInteger:
            context['paginator'] = paginator.page(1)
        except EmptyPage:
            context['paginator'] = paginator.page(paginator.num_pages)
        
        return context



class SearchReviewsView(TemplateView):
    template_name = "search/reviews.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_reviews'] = AbstractReview.latest_reviews()
        
        query = kwargs.get('query')
        query = urllib.parse.unquote(query)
        query = urllib.parse.unquote_plus(query)
        context['query'] = query

        reviews = search_reviews(query)
        context['reviews_count'] = len(reviews)

        page = self.request.GET.get('page', 1)
        paginator = Paginator(reviews, 10)
        try:
            context['paginator'] = paginator.page(page)
        except PageNotAnInteger:
            context['paginator'] = paginator.page(1)
        except EmptyPage:
            context['paginator'] = paginator.page(paginator.num_pages)
        return context


class SearchPhotosView(TemplateView):
    template_name = "search/photos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_reviews'] = AbstractReview.latest_reviews()
        
        query = kwargs.get('query')
        query = urllib.parse.unquote(query)
        query = urllib.parse.unquote_plus(query)
        context['query'] = query

        photos = search_photos(query)
        context['photos_count'] = photos.count()

        page = self.request.GET.get('page', 1)
        paginator = Paginator(photos, 10)
        try:
            context['paginator'] = paginator.page(page)
        except PageNotAnInteger:
            context['paginator'] = paginator.page(1)
        except EmptyPage:
            context['paginator'] = paginator.page(paginator.num_pages)
        
        return context


class SearchView(TemplateView):
    template_name = "search/index.html"
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['recent_reviews'] = AbstractReview.latest_reviews()
        context['featured_tour_operators'] = TourOperator.objects.filter(slug__isnull=False).exclude(slug='').order_by('-date_created')[:4]
        query = kwargs.get('query')
        query = urllib.parse.unquote(query)
        query = urllib.parse.unquote_plus(query)
        if len(query) <= 3:
            context['error'] = 'Your search must be at least 4 characters'
            return context

        #LOG
        search_log = SearchLog()
        search_log.query = query
        if not self.request.user.is_anonymous:
            search_log.user = self.request.user
        visitor_data = get_visitor_data(self.request)
        search_log.ip_address = visitor_data['ip_address']
        search_log.device_type = visitor_data['device_type']
        search_log.browser_type = visitor_data['browser_type']
        search_log.browser_version = visitor_data['browser_version']
        search_log.os_type = visitor_data['os_type']
        search_log.os_version = visitor_data['os_version']
        search_log.save()
        #END LOG
        
        context['query'] = query

        tour_operators = search_tour_operators(query)
        context['tour_operators'] = tour_operators[:3]
        context['tour_operators_count'] = tour_operators.count()

        #itineraries
        packages = search_tour_packages(query)
        context['packages'] = packages[:3]
        context['packages_count'] = packages.count()

        #articles
        any_name = Q()
        for bit in query.split():
            any_name &= (
                Q(title__lower__icontains=bit.lower()) |
                Q(title_short__lower__icontains=bit.lower()) |
                Q(highlights__lower__icontains=bit.lower())
            )
        articles = Article.objects.filter(any_name)
        context['articles'] = articles[:3]
        context['articles_count'] = articles.count()

        #countries
        any_name = Q()
        for bit in query.split():
            any_name &= (
                Q(name__lower__icontains=bit.lower()) |
                Q(name_short__lower__icontains=bit.lower())
            )
        countries = CountryIndex.objects.filter(any_name)
        context['countries'] = countries[:3]
        context['countries_count'] = countries.count()

        #parks
        any_name = Q()
        for bit in query.split():
            any_name &= (
                Q(name__lower__icontains=bit.lower()) |
                Q(name_short__lower__icontains=bit.lower())
            )
        parks = Park.objects.filter(any_name)
        context['parks'] = parks[:3]
        context['parks_count'] = parks.count()

        #photos
        photos = search_photos(query)
        context['photos'] = photos[:3]
        context['photos_count'] = len(photos)

        #articles
        articles = search_articles(query)
        context['articles'] = articles[:3]
        context['articles_count'] = articles.count()

        #reviews
        reviews = search_reviews(query)
        context['reviews'] = reviews[:3]
        context['reviews_count'] = len(reviews)
        
        return context
