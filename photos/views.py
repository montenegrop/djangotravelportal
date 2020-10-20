from django.conf import settings
from django.views.generic.detail import DetailView
from django.views.generic import UpdateView
from uuid import uuid4
from django.views.generic import TemplateView
from django.views.generic.base import View
from django.middleware import csrf
from operators.models import Itinerary
from django.core import serializers
from photos.models import Photo, Comment
from places.models import Animal, Activity, Park, CountryIndex
from photos.models import Tag
from django.urls import reverse
from .forms import CommentForm, PhotoSearchForm, PhotoTagsForm
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from users.models import User, UserProfile
from analytics.models import Action
from datetime import datetime
from django.contrib.contenttypes.models import ContentType
import random
import json
from django.forms.models import model_to_dict
from django.shortcuts import render, get_object_or_404
from core.utils import get_thumbnailer_
from rest_framework.views import APIView
from rest_framework.response import Response
import os.path
import math
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.utils.decorators import method_decorator
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from PIL import Image
from analytics.utils import log_action
from photos.photos_json import photo_to_json
import math


@method_decorator(csrf_exempt, name='dispatch')
class PhotoLikeView(View):

    def post(self, request, **kwargs):
        try:
            photo = Photo.objects.get(pk=self.kwargs.get("pk"))
        except:
            return JsonResponse({'message': 'Photo not found'})
        kudu_count = photo.kudu_count
        if kudu_count == 1:
            person_text = "Person"
        else:
            person_text = "People"
        text = "%s gave this<br />a kudu" % person_text
        if request.user.id is None:
            return JsonResponse({'message': 'You will need to sign in', 'kudus': kudu_count, 'text': text})
        else:
            if Action.objects.filter(action_type="K", user=request.user, content_type__model='photo', photo=photo).count():
                return JsonResponse(
                    {'message': 'Thanks, but you already gave a kudu', 'kudus': kudu_count, 'text': text})
            else:
                action = Action()
                action.content_type = ContentType.objects.get(model='photo')
                action.object_id = photo.id
                action.content_object = photo
                action.user = request.user
                action.action_type = 'K'
                action.save()
                photo.update_kudu_count()
                photo.check_and_send_kudu_email()
                if photo.kudu_count == 1:
                    person_text = "Person"
                else:
                    person_text = "People"
                text = "%s gave this<br />a kudu" % person_text
                message = "Thank you for giving a kudu"
                return JsonResponse({'message': message, 'kudus': photo.kudu_count, 'text': text})


class PhotosAPIView(APIView):
    def post(self, request, **kwargs):
        data = request.data
        photos = Photo.objects.filter(draft=False, date_deleted__isnull=True)
        response = {}
        # filters
        if data.get('username', '') != '':
            user = User.objects.get(username=data.get('username'))
            photos = photos.filter(user=user)
        if data.get('animal', '') != '':
            animal = Animal.objects.get(slug=data.get('animal'))
            photos = photos.filter(animals__slug=data.get('animal'))
        if data.get('country', '') != '':
            photos = photos.filter(country_index__slug=data.get('country'))
        if data.get('activity', '') != '':
            photos = photos.filter(activity__slug=data.get('activity'))
        if data.get('itinerary', '') != '':
            photos = photos.filter(itinerary__slug=data.get('itinerary'))
        if data.get('park', '') != '':
            try:
                park = Park.objects.get(slug__lower=data.get('park').lower())
                if park:
                    photos = photos.filter(park=park)
            except Park.DoesNotExist:
                pass
        # limit
        if data.get('current_page', '') == '':
            current_page = 1
        else:
            current_page = int(data.get('current_page', 1))

        limit_1 = ((current_page - 1) * 21)
        limit_2 = limit_1 + 21

        response = photo_to_json(request, response, photos, limit_1, limit_2)

        return Response(response)


class PhotosView(View):
    template_name = "photos/photos.html"

    def get(self, request, **kwargs):
        return self.post(request, **kwargs)

    def post(self, request, **kwargs):
        context = {}
        photos = Photo.objects.filter(draft=False, date_deleted__isnull=True)
        context['vue_variables'] = {}
        context['vue_strings'] = {}
        # selected items
        page_count = math.floor(photos.count() / 21)
        context['vue_variables']['page_count'] = page_count
        context['vue_variables']['activity_selected'] = None
        context['vue_variables']['country_selected'] = None
        context['vue_variables']['animal_selected'] = None
        context['vue_variables']['park_selected'] = None
        context['vue_strings']['csrf_token'] = csrf.get_token(request)
        if self.request.GET.get('park'):
            try:
                park = Park.objects.get(slug__lower=self.request.GET.get('park').lower())
                if park:
                    context['vue_variables']['park_selected'] = str(park.pk)
            except Park.DoesNotExist:
                pass
            # try:
            #     activity = Activity.objects.get(slug__lower=self.request.GET.get('activity').lower())
            #     if activity:
            #         context['vue_variables']['activity_selected'] = str(activity.pk)
            # except activity.DoesNotExist:
            #     pass

        animals = Animal.objects.all().order_by("name").values('slug', 'name')
        context['vue_variables']['animals_json'] = json.dumps(list(animals))

        activities = Activity.objects.all().values('slug', 'name')
        context['vue_variables']['activities_json'] = json.dumps(list(activities))

        countries = CountryIndex.objects.all()
        countries_parks = []
        for country in countries:
            country_park = {}
            country_park['slug'] = country.slug
            country_park['name'] = country.name
            country_park['parks'] = [x[0] for x in country.parks.all().values_list('slug')]
            countries_parks.append(country_park)
        context['vue_variables']['countries_json'] = json.dumps(
            list(countries_parks))
        photos_count = photos.count()
        context['photos_count'] = photos_count
        parks = Park.objects.all().values('slug', 'name')
        context['vue_variables']['parks_json'] = json.dumps(list(parks))
        return render(request, self.template_name, context=context)


class PhotoDetailView(TemplateView):
    model = Photo
    template_name = "photos/photo.html"
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        photo = Photo.objects.get(pk=self.kwargs.get('pk'))
        related_images = Photo.objects.all().filter(
            user=photo.user).exclude(id=photo.pk).order_by('?')
        context["user_images"] = related_images[:3]
        comments = Comment.objects.all().filter(
            content_type__model='Photo',
            object_id=photo.pk)[::-1]
        context["comments"] = comments
        context["object"] = photo
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if len(form['comment'].value()) > 0:
            comment_text = form['comment'].value()
            a = Comment(comment=comment_text,
                        content_type=ContentType.objects.get(
                            app_label="photos", model="Photo"),
                        user=request.user,
                        content_object=self.get_object(),
                        user_profile=UserProfile.objects.all().filter(user=request.user)[0])
            a.save()
        return HttpResponseRedirect(request.path)


class PhotoLoadAjax(DetailView):
    model = Photo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['country_indexes'] = CountryIndex.objects.all()
        context['activities'] = Activity.objects.filter(activity_type="SAFARI")
        context['animals'] = Animal.objects.all().order_by('name')

        return context

    def get_template_names(self):
        return ["photos/photo_card_for_reviews.html"]


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class PhotoDeleteView(TemplateView):
    model = Photo

    def get(self, request, pk, **kwargs):
        photo = get_object_or_404(Photo, pk=pk)
        if photo.user == request.user or photo.tour_operator == request.user.profile.tour_operator:
            photo.date_deleted = datetime.today()
            photo.save()
            return HttpResponse('Photo deleted')
        from django.http import Http404
        raise Http404("Not your photo")


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class PhotoCaptionView(TemplateView):
    model = Photo

    def get(self, request, pk, **kwargs):
        photo = get_object_or_404(Photo, pk=pk, user=request.user)
        if len(request.GET.get('caption')) > 100:
            return HttpResponse('Your comment is too long')
        else:
            photo.caption = request.GET.get('caption')
            photo.save()
            return HttpResponse('Caption saved')


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class PhotoTagView(UpdateView):
    model = Photo
    template_name = 'photos/photo_tag.html'
    form_class = PhotoTagsForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        photo = get_object_or_404(Photo, pk=self.kwargs.get('pk'), user=self.request.user)

        context['photo'] = photo
        context['return_url'] = self.get_success_url()
        return context

    def get_success_url(self):
        if self.object.park_review:
            return reverse('reviews:park_review_manage_photos', kwargs={'pk': self.object.park_review.id})
        else:
            return reverse('reviews:tour_operator_manage_photos', kwargs={'pk': self.object.tour_operator_review.id})


def load_parks(request):
    country_id = request.GET.get('country')
    parks = Park.objects.filter(country_indexes__id=country_id).order_by('name')
    return render(request, 'photos/park_dropdown_list_options.html', {'parks': parks})

@method_decorator(login_required, name='dispatch')
class PhotoSaveView(TemplateView):
    model = Photo
    template_name = "photos/add_photos.html"

    def post(self, request, *args, **kwargs):
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
        return HttpResponse('photos/add-photos')

@method_decorator(login_required, name='dispatch')
class PhotoAddView(TemplateView):
    model = Photo
    template_name = "photos/add_photos.html"

    def get_context_data(self, **kwargs):
        photo_id = int(self.request.GET.get('photo', 0))
        # photo_id = next((value for key, value in self.request.GET.items() if 'photo_id' in key), 0)
        context = super().get_context_data(**kwargs)
        if self.request.GET.get('to', ''):
            context['is_to'] = int(self.request.GET.get('to', ''))

        context['country_indexes'] = CountryIndex.objects.all()
        context['activities'] = Activity.objects.filter(activity_type="SAFARI")
        context['animals'] = Animal.objects.all().order_by('name')
        context['edit_photo_id'] = photo_id
        context['previous_url'] = self.request.META.get('HTTP_REFERER')
        context['max_photo_count'] = 10
        from django.urls import reverse
        context['cancel_url'] = reverse('backend:member_photos')
        #context['submit_url'] = reverse('photos:save_photos', kwargs={'pk': self.request.user.id})
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class UserCreatePhotoView(APIView):
    template_name = "photos/add_photos.html"

    def get(self, **kwargs):
        if 'pk' in kwargs:
            itinerary = Itinerary.objects.filter(pk=self.kwargs.get('pk'))
            itinerary = itinerary.filter(tour_operator=self.request.user.profile.tour_operator)
            itinerary = itinerary.first()

        context = super().get_context_data(**kwargs)
        context['max_photo_count'] = 10
        render(request, self.template_name, context=context)

    def post(self, request, **kwargs):
        im = Image.open(request.FILES.get('file'))
        width, height = im.size
        if width < 720 or height < 540:
            return HttpResponseBadRequest('Image is too small')
        else:
            itinerary = False
            if 'itinerary_slug' in kwargs:
                itinerary_slug = self.kwargs.get('itinerary_slug')
                itineraries = Itinerary.objects.filter(slug=itinerary_slug)
                itineraries = itineraries.filter(tour_operator=self.request.user.profile.tour_operator)
                itinerary = itineraries.first()
            photo = Photo(draft=True)
            to = self.request.GET.get('to', -1)
            if not to:
                to = 0
            to = int(to)
            if to == 1:
                photo.tour_operator = self.request.user.profile.tour_operator
            else:
                photo.user = request.user

            if itinerary:
                photo.itinerary = itinerary
            photo.image = request.FILES.get('file')

            if photo.image.size > settings.MAX_PHOTO_SIZE:
                resize_factor = math.sqrt(photo.image.size / settings.MAX_PHOTO_SIZE)
                new_width = int(photo.image.width / resize_factor)
                new_height = int(photo.image.height / resize_factor)
                output_size = (new_width, new_height)
                img = Image.open(photo.image.path)
                new_size = img.resize(output_size)
                new_size.save(photo.image.path)


            photo.uuid = uuid4().hex
            photo.save()
            return Response(photo.id)


class PhotoAddAckView(TemplateView):
    template_name = "photos/add_photos_ack.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        to = -1
        if self.request.GET.get('to', ''):
            to = int(self.request.GET.get('to', ''))
        if to == 1:
            context['cancel_url'] = reverse('backend:tour_operator_photos')
        if to == 0:
            context['cancel_url'] = reverse('backend:member_photos')
        return context
