from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from places.models import Animal, CountryIndex, Park, Activity, Currency, Country
from django.views.generic.detail import DetailView
from blog.models import Article
from users.models import UserProfile
from core.utils import auto_link
from reviews.models import AbstractReview, TourOperatorReview, ParkReview
from photos.models import Photo
from operators.models import TourOperator, Itinerary
from itertools import chain
from core.utils import *
from django.db.models import Count, Avg, Case, When, Value
from statistics import mode
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache.utils import make_template_fragment_key
from django.core.cache import cache
import json
from django.core import serializers
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.template import Template, Context
from analytics.utils import log_action
from django.views.generic.base import View
from analytics.models import Action
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache

class WildlifeView(TemplateView):
    template_name = "places/wildlife.html"

    def get_context_data(self, **kwargs):
        context = {}
        log_action(self.request)
        if cache.get('WildlifeView'):
            context.update(cache.get('WildlifeView'))
            return context
        animals = Animal.objects.all().order_by('name')
        context['animals'] = animals
        header_image = "{0}{1}".format(settings.BASE_URL, animals.get(name__lower='bushbaby').image.url)
        context['header_image'] = header_image
        cache.set('WildlifeView', context)
        return context


class ParksRollupView(TemplateView):
    template_name = "places/parks_rollup.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page', 1)
        parks = Park.objects.all()
        paginator = Paginator(parks, 10)
        try:
            context['parks'] = paginator.page(page)
        except PageNotAnInteger:
            context['parks'] = paginator.page(1)
        except EmptyPage:
            context['parks'] = paginator.page(paginator.num_pages)
        context['parks_count'] = parks.count()
        context['recent_reviews'] = ParkReview.latest_reviews()
        articles = Article.objects.order_by('-date_created')[:3]
        context['recent_articles'] = articles
        context['image'] = Park.objects.filter(slug='buffalo-springs').first().image.url
        log_action(self.request)
        return context


class SwahiliView(TemplateView):
    template_name = "places/swahili.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        log_action(self.request)
        return context


class ActivitiesView(TemplateView):
    template_name = "places/activities.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activities = Activity.objects.all().order_by('name')
        context['activities'] = activities
        bw = activities.get(slug__lower='bird-watchingwith-professional-guide')
        header_image = "{0}{1}".format(settings.BASE_URL, bw.image.url)
        context['header_image'] = header_image
        log_action(self.request)
        return context


class GuidesView(TemplateView):
    template_name = "places/guides.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parks = Park.objects.all().order_by('name')
        parks_by_country_count = {}
        parks_by_country = {}
        context['reviews_by_parks'] = {}
        for park in parks:
            context['reviews_by_parks'][park.pk] = ParkReview.objects.filter(
                park__pk=park.pk).count()
            for country in park.country_indexes.all():
                parks_by_country.setdefault(country.pk, []).append(park)
                if country.pk in parks_by_country_count:
                    parks_by_country_count[country.pk] += 1
                else:
                    parks_by_country_count[country.pk] = 1
        context['parks'] = parks
        context['parks_by_country'] = parks_by_country
        context['parks_by_country_count'] = parks_by_country_count
        # operators stats
        operators_by_country_count = {}
        countries = CountryIndex.objects.all()
        for country in countries:
            operators = TourOperator.objects.filter(date_deleted__isnull=True).filter(
                country_indexes__pk=country.pk).count()
            operators_by_country_count[country.pk] = operators
        context['operators_by_country_count'] = operators_by_country_count
        # reviews
        reviews = AbstractReview.latest_reviews()
        context['reviews'] = reviews
        # recent operators
        operators = TourOperator.latest_added()
        context['operators'] = operators
        # stats
        context['tour_operators_count'] = get_tour_operators_count()
        context['tour_packages_count'] = get_tour_packages_count()
        context['reviews_count'] = get_reviews_count()
        context['parks_count'] = get_parks_count()
        context['users_count'] = get_users_count()
        context['photos_count'] = get_photos_count()
        context['wildlife_count'] = get_wildlife_count()
        context['countries_count'] = get_countries_count()
        countries = CountryIndex.objects.all()
        context['countries_1'] = countries[:5]
        context['countries_2'] = countries[5:10]
        context['countries_3'] = countries[10:]
        log_action(self.request)
        return context


class AnimalDetailView(DetailView):
    model = Animal
    template_name = "places/animal.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        articles = Article.objects.filter(animals=self.object).order_by('-date_created')[:3]
        context['articles'] = articles
        reviews_tour = TourOperatorReview.objects.filter(animals=self.object).order_by('?')[:2]
        reviews_park = ParkReview.objects.filter(animals=self.object).order_by('?')[:2]
        reviews = chain(reviews_park, reviews_tour)
        context['reviews'] = reviews
        total_photos = Photo.objects.filter(draft=False, date_deleted__isnull=True).filter(
            animals__id=self.object.pk).count()
        photos = Photo.objects.filter(draft=False, date_deleted__isnull=True).filter(animals=self.object).order_by('?')
        count = photos.count()
        if count <= 5:
            photos = photos[:3]
        elif count >= 6 and count < 9:
            photos = photos[:6]
        else:
            photos = photos[:9]
        context['photos'] = photos
        context['total_photos'] = total_photos
        # parks
        parks = self.object.parks.filter(safari_suitability__gte=9)
        if parks:
            context['parks_1'] = parks[:5]
            context['parks_2'] = parks[5:10]
        log_action(self.request, hit_object=self.object)
        return context

    def get_object(self, queryset=None):
        obj = super(AnimalDetailView, self).get_object(queryset=queryset)
        if obj.highlights:
            elements = obj.highlights.strip().split("\n")
            string = "<ul>\n"
            string += "\n".join(["<li>" + str(s) + "</li>" for s in elements])
            string += "\n</ul>"
            obj.highlights = string
        obj.description = auto_link(obj.description)
        return obj


class CountryIndexDetailView(DetailView):
    model = CountryIndex
    template_name = "places/country_index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        country_index = context['object']
        operators = TourOperator.objects.filter(country_indexes=country_index)
        context['companies'] = operators.count()
        itineraries = Itinerary.objects.filter(country_indexes=country_index)
        context['tours'] = itineraries.count()
        animals = Animal.objects.filter(country_indexes=country_index)
        context['parks'] = country_index.parks.count()
        context['country_data'] = serializers.serialize('json', [country_index],
                                                        fields=('name', 'slug', 'latitude', 'longitude'))
        context['parks_data'] = serializers.serialize('json', Park.objects.all(),
                                                      fields=('name', 'name_short', 'latitude', 'longitude', 'slug'))
        vaccinations = country_index.vaccinations.all()
        context['vaccinations_1'] = vaccinations[:2]
        context['vaccinations_2'] = vaccinations[2:4]
        context['vaccinations_3'] = vaccinations[4:]
        context['highlighted_articles'] = country_index.article_set.order_by('-date_created')[0:2].all()
        context['highlighted_activities'] = country_index.activities.all().order_by('name')[:6]
        context['highlighted_animals'] = animals.order_by('-priority')[:6]
        context['animals_count'] = animals.count()
        context['latest_photos'] = country_index.photos.order_by('-date_created')[0:1].all()
        context['latest_photos_count'] = Photo.objects.filter(draft=False, country_index=country_index,
                                                              date_deleted__isnull=True).distinct().count()
        context['airports'] = country_index.airports.replace(",", ", ")

        # /// If we stop using the currency JS
        # coins = []
        # for currency in Currency.objects.all():
        #     country = Country.objects.filter(currency_code=currency.code).first()
        #     coin = {'country': country,
        #             'code': currency.code,
        #             'rate': currency.usd_exchange_rate,
        #             'flag': country.flag_flat}
        #     coins.append(coin)

        # context['currency'] = {'name': country.currency_name, 'code': country.currency_code}
        # context['coins'] = coins
        # ///

        return context


class CountryIndexParksDetailView(DetailView):
    model = CountryIndex
    template_name = "places/country_index_parks.html"

    def get_context_data(self, **kwargs):
        context = kwargs

        country_index = context['object']

        context['country_data'] = serializers.serialize('json', [country_index],
                                                        fields=('name', 'slug', 'latitude', 'longitude'))

        context['parks_data'] = serializers.serialize('json', Park.objects.all(),
                                                      fields=('name', 'name_short', 'latitude', 'longitude', 'slug'))
        context['latest_photos'] = country_index.photos.order_by('-date_created')[0:1].all()
        context['latest_photos_count'] = Photo.objects.filter(draft=False, country_index=country_index,
                                                              date_deleted__isnull=True).distinct().count()
        context['highlighted_articles'] = country_index.article_set.order_by('-date_created')[0:2].all()
        context['highlighted_activities'] = country_index.activities.all().order_by('?')[:6]
        animals = Animal.objects.filter(country_indexes=country_index)
        context['highlighted_animals'] = animals.order_by('?')[:6]
        context['animals_count'] = animals.count()

        context['object'].header_caption_link = context['object'].header_caption_link or ""
        context['object'].highlighted_articles = context['object'].article_set.order_by('-date_created')[0:2].all()
        for article in context['object'].highlighted_articles:
            article.categories_string = ", ".join([category.name for category in article.categories.all()])
        context['object'].highlighted_activities = context['object'].activities.order_by('name')[0:6]
        context['object'].highlighted_animals = context['object'].animal_set.order_by('-priority')[0:6]
        context['object'].highlighted_photo = context['object'].photos.order_by('-date_created')[0]
        context['object'].parksannotated = context['object'].parks.order_by('name').prefetch_related('park_reviews').annotate(
            parkreview_count=Count('park_reviews', distinct=True)).annotate(
            photo_count=Count('photos', distinct=True)).annotate(
            parkreview_average=Avg('park_reviews__overall_rating')).all()

        for park in context['object'].parksannotated:
            park.tour_operators_cnt = park.tour_operators.all().count()
            park.tour_packages_cnt = Itinerary.objects.filter(parks__in=[park]).count()
            park.reviews_cnt = park.parkreview_count
            park.photos_cnt = Photo.objects.filter(draft=False, park=park, date_deleted__isnull=True).distinct().count()

        for article in context['object'].highlighted_articles:
            article.categories_string = ", ".join([category.name for category in article.categories.all()])
        log_action(self.request, hit_object=self.object)
        return context


class ParkActivitiesDetailView(DetailView):
    model = Park
    template_name = "places/activities.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activities = context['object'].activities.all().order_by('name')
        activities = activities.filter(image__isnull=False)
        context['activities'] = activities
        header_image = "{0}{1}".format(settings.BASE_URL, activities.get(slug__lower='bird-watchingwith-professional-guide').image.url)
        context['header_image'] = header_image
        context['isCountryActivities'] = False
        log_action(self.request, hit_object=self.object)
        return context


class CountryIndexActivitiesDetailView(DetailView):
    model = CountryIndex
    template_name = "places/activities.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activities = context['object'].activities.all().order_by('name')
        activities = activities.filter(image__isnull=False)
        context['activities'] = activities
        header_image = "{0}{1}".format(settings.BASE_URL, activities.get(slug__lower='bird-watchingwith-professional-guide').image.url)
        context['header_image'] = header_image
        context['isCountryActivities'] = True
        log_action(self.request, hit_object=self.object)
        return context


class ParkWildlifeDetailView(DetailView):
    model = Park
    template_name = "places/park_wildlife.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        park = context['object']
        animals = Animal.objects.filter(parks=park)
        context['animals'] = animals.order_by('name')
        log_action(self.request, hit_object=self.object)
        return context


class CountryIndexWildlifeDetailView(DetailView):
    model = CountryIndex
    template_name = "places/country_index_wildlife.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        country_index = context['object']
        animals = Animal.objects.filter(country_indexes=country_index)
        context['animals'] = animals.order_by('name')
        log_action(self.request, hit_object=self.object)
        return context


class CountryIndexPhotosDetailView(DetailView):
    model = CountryIndex
    template_name = "places/country_index_photos.html"


class CountryIndexGettingThereDetailView(DetailView):
    model = CountryIndex
    template_name = "places/country_index_getting_there.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        country_index = context['object']
        operators = TourOperator.objects.filter(country_indexes=country_index)
        context['companies'] = operators.count()
        itineraries = Itinerary.objects.filter(country_indexes=country_index)
        context['tours'] = itineraries.count()
        animals = Animal.objects.filter(country_indexes=country_index)
        context['parks'] = country_index.parks.count()
        context['country_data'] = serializers.serialize('json', [country_index],
                                                        fields=('name', 'slug', 'latitude', 'longitude'))
        context['parks_data'] = serializers.serialize('json', Park.objects.all(),
                                                      fields=('name', 'name_short', 'latitude', 'longitude', 'slug'))
        vaccinations = country_index.vaccinations.all()
        context['highlighted_articles'] = country_index.article_set.order_by('-date_created')[0:2].all()
        context['highlighted_activities'] = country_index.activities.all().order_by('name')[:6]
        context['highlighted_animals'] = animals.order_by('-priority')[:6]
        context['animals_count'] = animals.count()
        context['latest_photos'] = country_index.photos.order_by('-date_created')[0:1].all()
        context['latest_photos_count'] = Photo.objects.filter(draft=False, country_index=country_index,
                                                              date_deleted__isnull=True).distinct().count()
        context['airports'] = country_index.airports.replace(",", ", ")
        log_action(self.request, hit_object=self.object)
        return context


class ParkDetailView(DetailView):
    model = Park
    template_name = "places/park.html"

    def get_context_data(self, **kwargs):
        context = kwargs
        park = context['object']
        country_indexes = CountryIndex.objects.filter(parks__exact=park)
        context['countries'] = country_indexes
        country_index = country_indexes[0]
        if len(country_indexes) > 1:
            country_index2 = country_indexes[1]
            context['country2'] = country_index2
        context['country'] = country_index
        #
        #
        #
        # sidebar:
        context['sidebar'] = {}
        context['sidebar']['main_park'] = serializers.serialize('json', [park],
                                                                fields=('name', 'slug', 'latitude', 'longitude'))
        context['sidebar']['all_parks'] = serializers.serialize('json', Park.objects.exclude(id=park.id),
                                                                fields=(
                                                                'name', 'name_short', 'latitude', 'longitude', 'slug'))
        context['sidebar']['reviews'] = ParkReview.latest_reviews(park)
        context['sidebar']['nearby_parks'] = Park.objects.filter(country_indexes__in=country_indexes)
        context['sidebar']['articles'] = country_index.article_set.order_by('-date_created')[0:2].all()
        if len(country_indexes) > 1:
            context['sidebar']['articles2'] = country_index2.article_set.order_by('-date_created')[0:2].all()
        context['sidebar']['latest_photo'] = park.photos.order_by('-date_created').last()
        context['sidebar']['photos_count'] = Photo.objects.filter(draft=False, park=park,
                                                                  date_deleted__isnull=True).distinct().count()
        context['sidebar']['animals'] = park.animal_set.order_by('-priority')[0:6].all()
        context['sidebar']['animal_count'] = park.animal_set.all().count()
        context['sidebar']['activities'] = park.activities.order_by('name')[0:6].all()
        context['sidebar']['activity_count'] = park.activities.all().count()
        #
        #
        #
        # main-page-content:
        #
        #
        #
        # headers:

        #
        #
        #
        operator_count = context['object'].itineraries.all().values('tour_operator').distinct().count()
        context['object'].tour_operator_count = operator_count
        park_reviews = ParkReview.objects.filter(
            park__pk=context['object'].pk).all()
        number_of_reviews = 0
        wildlife_quality = 0
        lodging_quality = 0
        crowdness = 0
        visited_months = []
        for review in park_reviews:
            number_of_reviews += 1
            wildlife_quality += review.quality_wildlife_rating
            lodging_quality += review.quality_lodging_rating
            crowdness += review.crowdedness_rating
            visited_months.append(review.visit_date.strftime('%B'))
        if number_of_reviews > 0:
            context['object'].wildlife_quality = wildlife_quality / number_of_reviews
            context['object'].lodging_quality = lodging_quality / number_of_reviews
            context['object'].crowdness_rating = crowdness / number_of_reviews
            context['object'].most_visited_month = max(set(visited_months), key=visited_months.count)
        #
        #
        #
        # Highlights:
        context['object'].highlights = park.highlights.split('\n')
        context['highlighted_activities'] = context['object'].activities.all().order_by('?')[:6]
        log_action(self.request, hit_object=self.object)
        return context


@method_decorator(csrf_exempt, name='dispatch')
class ParkReviewKuduView(View):

    def post(self, request, **kwargs):

        try:
            obj = ParkReview.objects.get(pk=self.kwargs.get("pk"))
        except:
            return JsonResponse({'message': 'Review not found'})
        kudu_count = obj.kudu_count
        if kudu_count == 1:
            person_text = "Person"
        else:
            person_text = "People"
        text = "%s gave this<br />a kudu" % person_text


        if request.user.id is None:
            return JsonResponse({'message': 'You will need to sign in', 'kudus': kudu_count, 'text': text})
        else:
            if Action.objects.filter(action_type="K", user=request.user, park_review=obj).count():
                return JsonResponse(
                    {'message': 'Thanks, but you already gave a kudu', 'kudus': kudu_count, 'text': text})
            else:
                action = Action()
                action.content_type = ContentType.objects.get(model='parkreview')
                action.object_id = obj.id
                action.content_object = obj
                action.user = request.user
                action.action_type = 'K'
                action.save()

                obj.update_kudu_count()
                if obj.kudu_count == 1:
                    person_text = "Person"
                else:
                    person_text = "People"
                text = "%s gave this<br /> a kudu" % person_text
                message = "Thank you for giving a kudu"
                return JsonResponse({'message': message, 'kudus': obj.kudu_count, 'text': text})


class ParkReviewsDetailView(DetailView):
    model = Park
    template_name = "places/park_reviews.html"

    def get_context_data(self, *args, **kwargs):
        context = kwargs
        review_id_focus = self.request.GET.get('review', '')
        if not review_id_focus:
            review_id_focus = self.kwargs.get('review_pk', '')
        context['review_id_focus'] = review_id_focus
        if review_id_focus:
            review_focus = [ParkReview.objects.get(id=int(review_id_focus))]
            temp = get_template('places/park_inserts/park_reviews.html')
            result = temp.render({'reviews': review_focus, 'focused': True})
            context['review_focus'] = result
        else:
            review_id_focus = '0'

        park = context['object']
        country_indexes = CountryIndex.objects.filter(parks__exact=park)
        context['countries'] = country_indexes
        country_index = country_indexes[0]
        if len(country_indexes) > 1:
            country_index2 = country_indexes[1]
            context['country2'] = country_index2
            if len(country_indexes) > 2:
                country_index3 = country_indexes[2]
                context['country3'] = country_index3

        context['country'] = country_index
        #
        #
        #
        # sidebar:
        context['sidebar'] = {}
        context['sidebar']['main_park'] = serializers.serialize('json', [park],
                                                                fields=('name', 'slug', 'latitude', 'longitude'))
        context['sidebar']['all_parks'] = serializers.serialize('json', Park.objects.exclude(id=park.id),
                                                                fields=(
                                                                'name', 'name_short', 'latitude', 'longitude', 'slug'))
        context['sidebar']['reviews'] = ParkReview.latest_reviews(park)
        context['sidebar']['nearby_parks'] = Park.objects.filter(country_indexes__in=country_indexes)
        context['sidebar']['articles'] = country_index.article_set.order_by('-date_created')[0:2].all()
        if len(country_indexes) > 1:
            context['sidebar']['articles2'] = country_index2.article_set.order_by('-date_created')[0:2].all()
            if len(country_indexes) > 2:
                context['sidebar']['articles3'] = country_index3.article_set.order_by('-date_created')[0:2].all()

        context['sidebar']['latest_photo'] = park.photos.order_by('-date_created').last()
        context['sidebar']['photos_count'] = Photo.objects.filter(draft=False, park=park,
                                                                  date_deleted__isnull=True).distinct().count()
        context['sidebar']['animals'] = park.animal_set.order_by('-priority')[0:6].all()
        context['sidebar']['animal_count'] = park.animal_set.all().count()
        context['sidebar']['activities'] = park.activities.order_by('name')[0:6].all()
        context['sidebar']['activity_count'] = park.activities.all().count()
        #
        #
        #
        x = 'date_created'
        total_park_reviews = ParkReview.objects.filter(park__pk=context['object'].pk, ).exclude(
            id=int(review_id_focus)).order_by('-date_created').count()
        park_reviews = ParkReview.objects.filter(park__pk=context['object'].pk, ).exclude(
            id=int(review_id_focus)).order_by('-date_created').all()[:10]
        for review in park_reviews:
            user = review.user
            review.user_reviews = ParkReview.objects.filter(user__exact=user).count() \
                                  + TourOperatorReview.objects.filter(user__exact=user).count()
            review.profile_picture = review.user.profile.avatar.url
        context['reviews'] = park_reviews
        context['total_park_reviews'] = total_park_reviews
        log_action(self.request, hit_object=self.object)
        return context

    def post(self, request, *args, **kwargs):
        park = Park.objects.get(slug__exact=self.kwargs.get('slug'))

        review_id_focus = json.loads(request.body)['focus_review']

        if not review_id_focus:
            review_id_focus = 0

        is_sorting = json.loads(request.body)['is_sorting']
        order = int(json.loads(request.body)['sort'])
        limit = int(json.loads(request.body)['limit'])

        order_by = '-date_created'

        if order == 1:
            order_by = '-date_created'
        elif order == 2:
            order_by = 'date_created'
        elif order == 3:
            order_by = 'views_count'

        reviews_capped = False
        limit1 = 0 if is_sorting else limit - 10
        limit2 = limit
        total_reviews = ParkReview.objects.filter(
            park__pk=park.pk).count()

        reviews = ParkReview.objects.filter(
            park__pk=park.pk).exclude(
            id=int(review_id_focus)).order_by(order_by).all()[limit1:limit2]
        temp = get_template('places/park_inserts/park_reviews.html')
        result = temp.render({'reviews': reviews})

        if total_reviews <= limit2:
            reviews_capped = True

        dictionary = {'capped': reviews_capped, 'reviews': result}

        return HttpResponse(json.dumps(dictionary), content_type="application/json")


class ParkGettingThereDetailView(DetailView):
    model = Park
    template_name = "places/park_getting_there.html"

    def get_context_data(self, **kwargs):
        context = kwargs
        park = context['object']
        country_indexes = CountryIndex.objects.filter(parks__exact=park)
        context['countries'] = country_indexes
        country_index = country_indexes[0]
        if len(country_indexes) > 1:
            country_index2 = country_indexes[1]
            context['country2'] = country_index2
        context['country'] = country_index
        #
        #
        #
        # sidebar:
        context['sidebar'] = {}
        context['sidebar']['main_park'] = serializers.serialize('json', [park],
                                                                fields=('name', 'slug', 'latitude', 'longitude'))
        context['sidebar']['all_parks'] = serializers.serialize('json', Park.objects.exclude(id=park.id),
                                                                fields=(
                                                                'name', 'name_short', 'latitude', 'longitude', 'slug'))
        context['sidebar']['reviews'] = ParkReview.latest_reviews(park)
        context['sidebar']['nearby_parks'] = Park.objects.filter(country_indexes__in=country_indexes)
        context['sidebar']['articles'] = country_index.article_set.order_by('-date_created')[0:2].all()
        if len(country_indexes) > 1:
            context['sidebar']['articles2'] = country_index2.article_set.order_by('-date_created')[0:2].all()
        context['sidebar']['latest_photo'] = park.photos.order_by('-date_created').last()
        context['sidebar']['photos_count'] = Photo.objects.filter(draft=False, park=park,
                                                                  date_deleted__isnull=True).distinct().count()
        context['sidebar']['animals'] = park.animal_set.order_by('-priority')[0:6].all()
        context['sidebar']['animal_count'] = park.animal_set.all().count()
        context['sidebar']['activities'] = park.activities.order_by('name')[0:6].all()
        context['sidebar']['activity_count'] = park.activities.all().count()
        log_action(self.request, hit_object=self.object)
        return context


class ParkToursDetailView(DetailView):
    model = Park
    template_name = "places/park_tours.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        log_action(self.request, hit_object=self.object)
        return context


class ParkPhotosDetailView(DetailView):
    model = Park
    template_name = "places/park_photos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        log_action(self.request, hit_object=self.object)
        return context


class ParkTourOperatorsDetailView(DetailView):
    model = Park
    template_name = "places/park_tour_operators.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        log_action(self.request, hit_object=self.object)
        return context


class ActivityDetailView(TemplateView):
    model = Activity
    template_name = "places/activity.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activity = Activity.objects.get(slug=self.kwargs.get('slug'))
        context['activity'] = activity
        context['photos'] = Photo.objects.filter(draft=False, activity=activity).order_by('-date_modified')[:9]
        log_action(self.request, hit_object=activity)
        return context
