from datetime import datetime
import datetime as datetime_date
from django.urls import reverse

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView
# Create your views here.
from django.views.generic.base import View
from django.shortcuts import redirect, get_object_or_404
from social_core.utils import slugify
from PIL import Image

import places
from analytics.utils import get_visitor_data, get_country_by_ip
from operators.models import TourOperator
from places.models import Animal, Activity, Park, CountryIndex, Country
from photos.models import Tag
from reviews.forms import ParkReviewForm, TourOperatorReviewForm, ParkKilimanjaroReviewForm
from reviews.models import ParkReview, TourOperatorReview, SafariType, KilimanjaroParkReview
import json
from django.db.models.functions import Lower
import yas.settings as settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from photos.models import Photo

from photos.forms import PhotoTagsForm

# Authentication:
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class MemberRequiredLoginView(UserPassesTestMixin, LoginRequiredMixin):

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class PhotoGuidelinesView(TemplateView):
    template_name = 'reviews/photo_guidelines.html'


class ReviewIndexView(TemplateView):
    template_name = 'reviews/index.html'


class ReviewCreateView(MemberRequiredLoginView, TemplateView):
    template_name = 'reviews/create.html'

    def get(self, request, **kwargs):
        return self.post(request)

    def post(self, request, **kwargs):
        data = request.POST
        errors = {}

        if data:
            if data.get('review_type') == 'park':
                if data.get('selected_park') and data.get('selected_country'):
                    return redirect('reviews:park', pk=data.get('selected_park'))
                elif data.get('selected_park') or data.get('selected_country'):
                    errors['selected_country'] = 'Please select a country' if not data.get('selected_country') else None
                    errors['selected_park'] = 'Please select a park' if not data.get('selected_park') else None
                else:
                    errors['selected_country'] = 'Please select a country'
                    errors['selected_park'] = 'Please select a park'

            else:
                if data.get('review_type') == 'tour_operator':
                    if data.get('selected_tour_operator'):
                        return redirect('reviews:tour_operator', pk=data.get('selected_tour_operator'))
                    else:
                        errors['selected_tour_operator'] = 'Please select a tour operator'
                else:
                    errors['review_type'] = 'Select a review type'

        context = {}

        countries = CountryIndex.objects.all()
        countries_json = []
        for country in countries:
            country_json = {}
            country_json['id'] = country.id
            country_json['name'] = country.name
            country_json['parks'] = list(country.parks.all().values('id', 'name'))
            countries_json.append(country_json)

        tour_operators = TourOperator.objects.all().order_by(Lower('name'))
        tour_operators_json = []
        for tour_operator in tour_operators:
            tour_operator_json = {}
            tour_operator_json['id'] = tour_operator.id
            tour_operator_json['name'] = tour_operator.name
            tour_operators_json.append(tour_operator_json)

        context['vue_variables'] = {}
        context['vue_variables']['errors'] = json.dumps(errors)
        context['vue_variables']['countries_json'] = json.dumps(countries_json)
        context['vue_variables']['tour_operators_json'] = json.dumps(tour_operators_json)
        context['vue_variables']['data'] = json.dumps(data)

        context['vue_strings'] = {}
        context['vue_strings']['review_type'] = data.get('review_type') if data else None
        context['vue_strings']['selected_country'] = data.get('selected_country') if data else None
        context['vue_strings']['selected_park'] = data.get('selected_park') if data else None
        context['vue_strings']['selected_tour_operator'] = data.get('selected_tour_operator') if data else None

        return render(request, self.template_name, context=context)


class ReviewCreateParkReviewAckView(MemberRequiredLoginView,TemplateView):
    template_name = "reviews/create_park_review_ack.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        review = get_object_or_404(ParkReview, pk=self.kwargs.get('pk'))

        reviewed_parks = []

        for parkreview in self.request.user.parkreview_set.all():
            reviewed_parks.append(parkreview.id)

        similar_parks = Park.objects.filter(country_indexes__in=review.park.country_indexes.all()).exclude(
            pk=review.park.id)
        context['review'] = review
        context['park'] = review.park
        context['similar_parks'] = similar_parks

        context['review_count'] = review.park.park_reviews.filter(status="AC").count()
        context['review_rating'] = review.park.rating_decimal()
        context['base_url'] = settings.BASE_URL
        return context


class ReviewCreateTourOperatorReviewAckView(MemberRequiredLoginView,TemplateView):
    template_name = "reviews/create_tour_operator_review_ack.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        review = get_object_or_404(TourOperatorReview, pk=self.kwargs.get('pk'))

        reviewed_parks = []

        for parkreview in self.request.user.parkreview_set.all():
            reviewed_parks.append(parkreview.park.id)

        similar_parks = review.parks.exclude(pk__in=reviewed_parks)
        context['review'] = review
        context['tour_operator'] = review.tour_operator
        context['similar_parks'] = similar_parks
        context['base_url'] = settings.BASE_URL
        return context


class ReviewCreateParkReviewView(MemberRequiredLoginView,TemplateView):
    model = ParkReview
    template_name = "reviews/create_park_review.html"
    form_class = ParkReviewForm

    def get(self, request, **kwargs):
        return super(ReviewCreateParkReviewView, self).get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        park = get_object_or_404(Park, pk=self.kwargs.get('pk'))
        animals = Animal.objects.all().order_by('name')
        animals_json = []
        for animal in animals:
            animal_json = {}
            animal_json['id'] = animal.id
            animal_json['name'] = animal.name
            animals_json.append(animal_json)

        activities = Activity.objects.filter(activity_type="SAFARI").order_by('name')
        activities_json = []
        for activity in activities:
            activity_json = {}
            activity_json['id'] = activity.id
            activity_json['name'] = activity.name
            activities_json.append(activity_json)

        routes_to_climb_json = []
        for key, value in KilimanjaroParkReview.ROUTES_CHOICES:
            route_to_climb_json = {}
            route_to_climb_json['key'] = key
            route_to_climb_json['value'] = value
            routes_to_climb_json.append(route_to_climb_json)

        context['vue_variables'] = {}
        context['vue_variables']['animals_json'] = json.dumps(animals_json)
        context['vue_variables']['activities_json'] = json.dumps(activities_json)
        context['vue_variables']['routes_to_climb_json'] = json.dumps(routes_to_climb_json)
        context["park"] = park
        return context


class ReviewCreateParkKilimanjaroView(ReviewCreateParkReviewView):
    model = KilimanjaroParkReview

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ReviewCreateTourOperatorView(MemberRequiredLoginView,TemplateView):
    model = TourOperatorReview
    template_name = "reviews/create_tour_operator_review.html"
    form_class = ParkReviewForm

    def get(self, request, **kwargs):
        return super(ReviewCreateTourOperatorView, self).get(request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tour_operator = get_object_or_404(TourOperator, pk=self.kwargs.get('pk'))
        countries = tour_operator.country_indexes.all().order_by('name')
        # countries = CountryIndex.objects.all().order_by('name')
        countries_json = []
        for country in countries:
            country_json = {}
            country_json['id'] = country.id
            country_json['name'] = country.name
            country_json['parks'] = list(country.parks.all().values('id', 'name'))
            countries_json.append(country_json)

        animals = Animal.objects.all().order_by('name')
        animals_json = []
        for animal in animals:
            animal_json = {}
            animal_json['id'] = animal.id
            animal_json['name'] = animal.name
            animals_json.append(animal_json)

        activities = Activity.objects.filter(activity_type="SAFARI").order_by('name')
        activities_json = []
        for activity in activities:
            activity_json = {}
            activity_json['id'] = activity.id
            activity_json['name'] = activity.name
            activities_json.append(activity_json)

        safari_types = SafariType.objects.all()
        safari_types_json = []
        for safari_type in safari_types:
            safari_type_json = {}
            safari_type_json['id'] = safari_type.id
            safari_type_json['name'] = safari_type.name
            safari_types_json.append(safari_type_json)

        routes_to_climb_json = []
        for key, value in KilimanjaroParkReview.ROUTES_CHOICES:
            route_to_climb_json = {}
            route_to_climb_json['key'] = key
            route_to_climb_json['value'] = value
            routes_to_climb_json.append(route_to_climb_json)

        context['vue_variables'] = {}
        context['vue_variables']['booking_with_this_company'] = False
        context['vue_variables']['countries_json'] = json.dumps(countries_json)
        context['vue_variables']['animals_json'] = json.dumps(animals_json)
        context['vue_variables']['activities_json'] = json.dumps(activities_json)
        context['vue_variables']['safari_types_json'] = json.dumps(safari_types_json)
        context['vue_variables']['routes_to_climb_json'] = json.dumps(routes_to_climb_json)
        context["tour_operator"] = tour_operator
        context["countries"] = countries
        return context


@login_required
def save_review_park(request, pk):
    if request.method == 'POST':
        data = json.loads(request.body)

        data['date_created'] = datetime.now()
        data['date_modified'] = datetime.now()
        data['email_sent'] = False
        data['visit_date'] = datetime(data['visit_date_year'], data['visit_date_month'], 1)

        form = ParkReviewForm(data)
        form.instance.user = request.user
        park = get_object_or_404(Park, pk=pk)
        form.instance.park = park
        ip = get_visitor_data(request)['ip_address']
        form.instance.ip_address = ip
        try:
            iso = get_country_by_ip(ip)
            country = Country.objects.get(iso=iso)
            if country:
                form.instance.country_written = country
        except places.models.Country.DoesNotExist:
            pass

        if form.is_valid():
            form = form.save()
            form.slug = slugify(data['title'])

            obj = json.loads(request.body)
            for key in obj.get('selected_activities'):
                form.activities.add(Activity.objects.get(pk=key))

            for key in obj.get('selected_animals'):
                form.animals.add(Animal.objects.get(pk=key))
            form.save()
            send_review_thank_you_email(request, park.name)
            data = {'status': 'success', 'review_park': form.id}
            return JsonResponse(data)
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})


@login_required
def save_review_park_kilimanjaro(request, pk):
    if request.method == 'POST':
        data = json.loads(request.body)
        data['slug'] = slugify(data['title'])
        data['date_created'] = datetime.now()
        data['date_modified'] = datetime.now()
        data['email_sent'] = False
        data['visit_date'] = datetime(data['visit_date_year'], data['visit_date_month'], 1)

        form = ParkKilimanjaroReviewForm(data)
        form.instance.user = request.user
        park = Park.objects.get(pk=pk)
        form.instance.park = park
        ip = get_visitor_data(request)['ip_address']
        form.instance.ip_address = ip
        try:
            iso = get_country_by_ip(ip)
            country = Country.objects.get(iso=iso)
            if country:
                form.instance.country_written = country
        except places.models.Country.DoesNotExist:
            pass

        if form.is_valid():

            form = form.save()
            form.slug = slugify(data['title'])
            obj = json.loads(request.body)

            for key in obj.get('selected_activities'):
                form.activities.add(Activity.objects.get(pk=key))

            for key in obj.get('selected_animals'):
                form.animals.add(Animal.objects.get(pk=key))

            form.save()
            send_review_thank_you_email(request, park.name)
            data = {'status': 'success', 'review_park': form.id}
            return JsonResponse(data)
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})


def send_review_thank_you_email(request, item):
    email_to = request.user.email
    if not settings.REAL_EMAILS:
        email_to = settings.TESTING_EMAILS
    from post_office import mail
    context = {}
    context['member'] = request.user.profile.display_name_for_email()
    context['item'] = item
    mail.send(
        email_to,
        'Your African Safari <support@yourafricansafari.com>',
        template='review_thank_you',
        context=context,
    )


@login_required
def save_review_tour_operator(request, pk):
    if request.method == 'POST':
        data = json.loads(request.body)
        data['title'] = data['review_title']
        data['content'] = data['review_copy']
        data['pearls_of_wisdom'] = data['pearls_of_wisdom']
        data['friend_recommend'] = data['friend_recommend']
        data['reached_summit'] = data['reached_summit']
        data['take_medications'] = data['take_medications']
        data['route_to_climb'] = data['route_to_climb']
        if data['route_to_climb'] == "unselected" or data['route_to_climb'] == None:
            data['route_to_climb'] = None
        data['other_route_to_climb'] = data['other_route_to_climb']
        data['date_created'] = datetime.now()
        data['date_modified'] = datetime.now()
        if data['start_date_year'] > 0:
            data['start_date'] = datetime(data['start_date_year'], data['start_date_month'], 1)

        if data['is_kilimanjaro'] == True:
            data_kilimanjaro = data
            data_kilimanjaro['crowdedness_rating'] = data_kilimanjaro['crowdedness_rating_kilimanjaro']
            data_kilimanjaro['quality_wildlife_rating'] = 0
            data_kilimanjaro['quality_lodging_rating'] = 0
            data_kilimanjaro['content'] = data_kilimanjaro['content_kilimanjaro']
            data_kilimanjaro['visit_date'] = data['start_date']
            data_kilimanjaro['pearls_of_wisdom'] = data['pearls_of_wisdom_kilimanjaro']

        data['vehicle_rating'] = data['vehicle_rating']
        data['meet_and_greet_rating'] = data['meet_and_greet_rating']
        data['responsiveness_rating'] = data['responsiveness_rating']
        data['safari_quality_rating'] = data['safari_quality_rating']
        data['itinerary_quality_rating'] = data['itinerary_quality_rating']
        data['overall_rating'] = data['overall_rating']
        data['days_booked'] = data['days_booked'] or 0
        data['did_not_go'] = data['did_not_go']
        data['find_out'] = data['find_out']
        data['find_out_website'] = data['find_out_website']

        data['email_sent'] = False
        if data['is_kilimanjaro'] == True:
            data_kilimanjaro['email_sent'] = False

            form_kilimanjaro = ParkKilimanjaroReviewForm(data_kilimanjaro)
            form_kilimanjaro.instance.user = request.user

            form_kilimanjaro.instance.park = Park.objects.get(slug='kilimanjaro')
            ip = get_visitor_data(request)['ip_address']
            form_kilimanjaro.instance.ip_address = ip
            try:
                iso = get_country_by_ip(ip)
                country = Country.objects.get(iso=iso)
                if country:
                    form_kilimanjaro.instance.country_written = country
            except places.models.Country.DoesNotExist:
                pass
            
            if form_kilimanjaro.is_valid():
                form_kilimanjaro = form_kilimanjaro.save()
                form_kilimanjaro.slug = slugify(data['title'])
                obj = json.loads(request.body)

                for key in obj.get('selected_activities'):
                    form_kilimanjaro.activities.add(Activity.objects.get(pk=key))

                for key in obj.get('selected_animals'):
                    form_kilimanjaro.animals.add(Animal.objects.get(pk=key))

                form_kilimanjaro.save()
                data_kilimanjaro = {'status': 'success', 'review_park': form_kilimanjaro.id}
                # return JsonResponse(data_kilimanjaro)
            else:
                return JsonResponse({'status': 'error', 'errors': form_kilimanjaro.errors})

        form = TourOperatorReviewForm(data)
        form.instance.user = request.user
        tour_operator = TourOperator.objects.get(pk=pk)
        form.instance.tour_operator = tour_operator
        form.instance.tour_operator.last_review_date = datetime.now()
        form.instance.tour_operator.save()
        if data['safari_type_id'] != "" and data['safari_type_id'] != None:
            form.instance.safari_type = SafariType.objects.get(id=data['safari_type_id'])

        ip = get_visitor_data(request)['ip_address']
        form.instance.ip_address = ip
        try:
            iso = get_country_by_ip(ip)
            country = Country.objects.get(iso=iso)
            if country:
                form.instance.country_written = country
        except places.models.Country.DoesNotExist:
            pass


        if form.is_valid():
            review = form.save()
            review.slug = slugify(data['review_title'])

            obj = json.loads(request.body)
            for key in obj.get('selected_activities'):
                review.activities.add(Activity.objects.get(pk=key))

            for key in obj.get('selected_animals'):
                review.animals.add(Animal.objects.get(pk=key))

            for key in obj.get('selected_countries'):
                review.country_indexes.add(CountryIndex.objects.get(pk=key))

            for key in obj.get('selected_parks'):
                review.parks.add(Park.objects.get(pk=key))

            review.save()
            send_review_thank_you_email(request, tour_operator.name)
            data = {'status': 'success', 'review_tour_operator': review.id}
            return JsonResponse(data)
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})


class ParkReviewDetailView(DetailView):
    model = ParkReview
    template_name = "reviews/park_review.html"


class TourOperatorReviewDetailView(DetailView):
    model = TourOperatorReview
    template_name = "places/tour_operator_review.html"


def test_settings(user, review):
    if user.id == review.user.id:
        return True
    else:
        return False


@method_decorator(login_required, name='dispatch')
class TourOperatorReviewManagePhotosView(UserPassesTestMixin, DetailView):
    model = TourOperatorReview
    template_name = "reviews/tour_operators_review_photos.html"

    def test_func(self):
        tour_review_id = self.request.get_full_path().rsplit('/', 1)[1]
        tour_review = TourOperatorReview.objects.get(id=tour_review_id)
        return test_settings(self.request.user, tour_review)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        review = get_object_or_404(TourOperatorReview, pk=self.kwargs.get('pk'), user=self.request.user)

        context['country_indexes'] = CountryIndex.objects.all()
        context['activities'] = Activity.objects.filter(activity_type="SAFARI")
        context['animals'] = Animal.objects.all().order_by('name')

        context['review'] = review
        context['max_photo_count'] = 10
        return context

    def post(self, request, pk):
        photos = Photo.objects.filter(park_review__pk=pk)

        data = request.POST

        for photo in photos:

            photo.caption = data.__getitem__('caption_' + str(photo.id))

            photo.country_index = CountryIndex.objects.get(
                id=int(data.__getitem__('country_index_' + str(photo.id)))) if data.__getitem__(
                'country_index_' + str(photo.id)) else None

            photo.park = Park.objects.get(id=int(data.__getitem__('park_' + str(photo.id)))) if data.__getitem__(
                'park_' + str(photo.id)) else None

            photo.activity = Activity.objects.get(
                id=int(data.__getitem__('activity_' + str(photo.id)))) if data.__getitem__(
                'activity_' + str(photo.id)) else None

            photo.animals.clear()
            if data.getlist('animals_' + str(photo.id)):
                for animal in data.getlist('animals_' + str(photo.id)):
                    photo.animals.add(Animal.objects.get(id=int(animal)))

            photo.tags.clear()
            if data.getlist('tags_' + str(photo.id)):
                tags = data.getlist('tags_' + str(photo.id))[0].split(',')
                for tag in tags:
                    photo.tags.add(Tag.objects.get(name=tag))

            photo.save()

        return HttpResponse('uploaded park review')


@method_decorator(login_required, name='dispatch')
class ParkReviewManagePhotosView(UserPassesTestMixin, TemplateView):
    model = ParkReview
    template_name = "reviews/parks_review_photos.html"

    def test_func(self):
        park_review_id = self.request.get_full_path().rsplit('/', 1)[1]
        park_review = get_object_or_404(ParkReview, id=park_review_id)
        return self.request.user.pk == park_review.user.pk

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        review = get_object_or_404(ParkReview, pk=self.kwargs.get('pk'), user=self.request.user)

        context['country_indexes'] = CountryIndex.objects.all()
        context['activities'] = Activity.objects.filter(activity_type="SAFARI")
        context['animals'] = Animal.objects.all().order_by('name')

        context['review'] = review
        context['max_photo_count'] = 10
        return context

    def post(self, request, pk):
        data = request.POST
        photos = []
        for key in data.keys():
            if key.startswith('photo_id'):
                photos.append(data[key])

        for photoId in photos:

            photo = Photo.objects.get(id=photoId)

            photo.draft = False

            photo.caption = data.__getitem__('caption_' + photoId)

            photo.country_index = CountryIndex.objects.get(
                id=int(data.__getitem__('country_index_' + photoId))) if data.__getitem__(
                'country_index_' + photoId) else None

            photo.park = Park.objects.get(id=int(data.__getitem__('park_' + photoId))) if data.__getitem__(
                'park_' + photoId) else None

            photo.activity = Activity.objects.get(
                id=int(data.__getitem__('activity_' + photoId))) if data.__getitem__(
                'activity_' + photoId) else None

            photo.animals.clear()
            if data.getlist('animals_' + photoId):
                for animal in data.getlist('animals_' + photoId):
                    photo.animals.add(Animal.objects.get(id=int(animal)))

            photo.tags.clear()
            if data.getlist('tags_' + photoId):
                tags = data.getlist('tags_' + photoId)[0].split(',')
                for tag in tags:
                    tag_model, _ = Tag.objects.get_or_create(name=tag)
                    photo.tags.add(tag_model)

            photo.save()

        return HttpResponse('uploaded park review')


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class ParkReviewCreatePhotoView(TemplateView):
    model = ParkReview

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        review = get_object_or_404(ParkReview, pk=self.kwargs.get('pk'), user=self.request.user)

        context['review'] = review
        return context

    def post(self, request, pk, **kwargs):
        review = get_object_or_404(ParkReview, pk=pk, user=request.user)
        if review.photos.count == 10:
            return HttpResponseBadRequest('Max photos have been reached')
        im = Image.open(request.FILES.get('file'))
        width, height = im.size
        if width < 720 or height < 540:
            return HttpResponseBadRequest('Image is too small')
        else:
            photo = Photo()
            photo.park_review = review
            photo.image = request.FILES.get('file')
            photo.user = request.user
            photo.draft = True
            photo.save()
            return HttpResponse(photo.id)


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class TourOperatorReviewCreatePhotoView(TemplateView):
    model = TourOperatorReview

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        review = get_object_or_404(TourOperatorReview, pk=self.kwargs.get('pk'), user=self.request.user)

        context['review'] = review
        return context

    def post(self, request, pk, **kwargs):
        review = get_object_or_404(TourOperatorReview, pk=pk, user=request.user)
        if review.photos.count == 10:
            return HttpResponseBadRequest('Max photos have been reached')
        im = Image.open(request.FILES.get('file'))
        width, height = im.size
        if width < 720 or height < 540:
            return HttpResponseBadRequest('Image is too small')
        else:
            photo = Photo()
            photo.tour_operator_review = review
            photo.image = request.FILES.get('file')
            photo.user = request.user
            photo.draft = True
            photo.save()
            return HttpResponse(photo.id)
