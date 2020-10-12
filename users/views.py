from itertools import chain
from smtplib import SMTPException
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.views import generic
from urllib.parse import urlencode
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string, get_template
from django.views.generic import TemplateView
from reviews.models import ParkReview, TourOperatorReview
from users.forms import UserProfileForm, SignUpForm
from users.models import UserProfile
from photos.models import Photo
from django import forms
from django.http import JsonResponse, HttpResponse
import json
from django.conf import settings
from post_office import mail
from post_office.models import EmailTemplate
from .tokens import account_activation_token
from django.urls import reverse
from django.contrib import messages
from django.http import Http404
from django.db.models import Value
import requests
from django.utils.translation import ugettext as _
from operators.models import TourOperator, Itinerary
import json
from datetime import datetime
import base64
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.views import View

from django.db.models import ImageField
import random, os
from rest_framework.views import APIView



class ChangeProfileView(FormView):
    template_name = "core/change_profile.html"
    form_class = UserProfileForm
    model = UserProfile



class SignUpEmail(TemplateView):
    template_name = "users/signup_email.html"
    form_class = UserProfileForm
    model = UserProfile


class SignUp(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


def logout_view(request):
    logout(request)
    return redirect('/')


def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        data['username'] = data['email']
        form = SignUpForm(data)
        if form.is_valid():
            data_captcha = {
                'response': data.get('token'),
                'secret': settings.RECAPTCHA_SECRET_KEY
            }
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            resp = requests.post(
                'https://www.google.com/recaptcha/api/siteverify', data=data_captcha, headers=headers)
            result_json = resp.json()
            if not result_json.get('success'):
                data = {'status': 'danger',
                        'serverError': 'Cannot verify that you\'re a human'}
                return JsonResponse(data)

            # form validations
            screen_name = form.cleaned_data.get('screen_name')
            if ' ' in screen_name:
                data = {'status': 'danger',
                        'serverError': 'Screen name cannot contain spaces'}
                return JsonResponse(data)

            if User.objects.filter(username=screen_name).exists():
                data = {'status': 'danger',
                        'serverError': 'Screen name already exists'}
                return JsonResponse(data)

            user = form.save(commit=False)
            user.is_active = False
            user.username = screen_name
            user.save()

            #new_profile = UserProfile(
            #    user=user, screen_name=screen_name)
            #new_profile.save()
            # password = form.cleaned_data.get('password1')
            # user = authenticate(username=user.username, password=password)
            # login(request, user)
            user.profile.screen_name = screen_name
            user.profile.save()

            to_email = form.cleaned_data.get('email')
            context = {}
            context['member'] = screen_name
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            link = settings.BASE_URL + reverse('activate', kwargs={'uidb64': uid, 'token': token})
            context['link'] = link
            if not settings.REAL_EMAILS:
                to_email = settings.TESTING_EMAILS
            try:
                res = mail.send(
                    to_email,
                    'Your African Safari <support@yourafricansafari.com>',
                    template='registration_email',
                    context=context,
                    priority='now'
                )
            except SMTPException as e:
                data = {'status': 'danger',
                        'serverError': 'An unexpected error has occurred when sending the email confirmation. Please try again later.'}
                return JsonResponse(data)
            except Exception as e:
                data = {'status': 'danger',
                        'serverError': 'An unexpected error has occurred.'}
                return JsonResponse(data)
            if res:
                messages.success(request, 'Please confirm your email address to complete the registration.')
            else:
                messages.error(request, 'There was an error with your activation email, our team will look into it.')
            data = {'status': 'success'}
            return JsonResponse(data)
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
    else:
        messages.error(request, 'Activation link is invalid')
    base_url = reverse('activate_complete')
    return redirect(base_url)


class MemberView(DetailView):
    model = UserProfile
    template_name = "member.html"

    def get_object(self, queryset=None):
        obj = super(MemberView, self).get_object(queryset=queryset)

        if "slug" in self.kwargs and obj.display_name_slugged() != self.kwargs.get("slug"):
            raise Http404
        else:
            animals = list(obj.animals_seen.all().order_by('?')[:3])
            obj.animals = animals
            activities = list(obj.activities_enjoy.filter(activity_type="SAFARI").all().order_by('?')[:3])
            obj.activities = activities
            parks = list(obj.parks_visited.order_by('id').all())
            obj.parks_highlighted = parks[:3]
            obj.parks_rest = parks[3:]
            obj.parks_count = len(parks)
            touroperator_reviews = TourOperatorReview.objects.filter(user__exact=obj.user, status="AC")
            park_reviews = ParkReview.objects.filter(user__exact=obj.user, status="AC")
            obj.reviews = list(chain(park_reviews, touroperator_reviews))
            obj.reviews.sort(key=lambda x: x.date_created, reverse=True)
            countries = list(obj.countries_visited.all())
            obj.countries_highlighted = countries[:3]
            obj.countries_rest = countries[3:]
            obj.countries_count = len(countries)
            obj.photos = Photo.objects.filter(draft=False, user__exact=obj.user)[:9]
            obj.photos_total = Photo.objects.filter(draft=False, user__exact=obj.user).count()

            obj.contribution_count = len(obj.reviews) + \
                                     obj.user.article_set.filter(article_status="PUBLISHED").count()
            return obj

    def post(self, request, **kwargs):
        user_profile = UserProfile.objects.get(id=self.kwargs.get('pk'))
        limit = int(json.loads(request.body)['limit'])
        photos_capped = False
        limit2 = limit * 9
        limit1 = limit2 - 9
        total_photos = Photo.objects.filter(draft=False, user__exact=user_profile.user).all().count()
        photos = Photo.objects.filter(draft=False, user__exact=user_profile.user)[limit1: limit2]
        temp = get_template('users/includes/extra_photos.html')
        result = temp.render({'photos': photos})
        if total_photos <= limit2:
            photos_capped = True
        dictionary = {'capped': photos_capped, 'photos': result}
        return HttpResponse(json.dumps(dictionary), content_type="application/json")


def change_password(request):
    if request.method == 'POST':
        check_old_password = request.user.check_password(request.POST['old_password'])
        check_new_password = bool(
            31 > len(request.POST['new_password']) > 7 and type(
                request.POST['new_password'] == str))
        if check_old_password and check_new_password:
            request.user.set_password(request.POST['new_password'])
            request.user.save()
            update_session_auth_hash(request, request.user)
            response = {'password': 'password updated'}
        elif not check_old_password:
            response = {'password': 'Invalid old password'}
        elif not check_new_password:
            response = {'password': 'Invalid new password'}
        else:
            response = {'password': 'Invalid passwords'}
        return HttpResponse(json.dumps(response))


class ChangeAvatar(View):
    def post(self, request):
        data = request.POST['avatar']
        format_, imgstr = data.split(';base64,')
        ext = format_.split('/')[-1]
        avatar = ContentFile(base64.b64decode(imgstr))
        self.request.user.profile.avatar.save('avatar.' + ext, avatar, save=True)
        response = {'message': 'avatar changed'}
        return HttpResponse(json.dumps(response))


#favs
from django.views.generic import TemplateView
from rest_framework.response import Response
from users.logic.favs import *


class ActivateCompleteView(TemplateView):
    template_name = "users/activate_complete.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class ShortListView(TemplateView):
    template_name = "users/shortlist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tour_operators = get_to_favs(self.request)
        context['tour_operators'] = tour_operators
        itineraries = get_it_favs(self.request)
        context['itineraries'] = itineraries
        if itineraries.exists() or not tour_operators.exists():
            context['active_itineraries'] = 'active show'
            context['active_operators'] = ''
        else:
            context['active_itineraries'] = ''
            context['active_operators'] = 'active show'
        return context


class AddItineraryFavAPIView(APIView):

    def get(self, request, itinerary_pk):
        """
        Create a Fav
        TODO
        """
        counts = get_favs_count(request)
        if counts >= 10:
            return Response({'status':'error', 'message': 'You cannot add more than 10 items to your shortlists'})
        from django.shortcuts import get_object_or_404
        fav = Fav()
        if self.request.user.is_authenticated:
            fav.user = self.request.user
        else:
            if not 'uuid' in request.session: 
                request.session['uuid'] = str(uuid.uuid1())
            fav.uuid = request.session['uuid']
        fav.itinerary = get_object_or_404(Itinerary, pk = itinerary_pk)
        fav.save()
        return Response({'status':'ok', 'count': counts + 1})

class DeleteItineraryFavAPIView(APIView):

    def get(self, request, itinerary_pk):
        """
        Delete a Fav
        set date_deleted = now
        TODO
        """
        favs = get_favs(request)
        favs = favs.filter(itinerary__pk=itinerary_pk)
        if favs.exists():
            for fav in favs.all():
                fav.date_deleted = datetime.today()
                fav.save()
        return Response({'status':'ok', 'count': get_favs_count(request), 'count_it' : get_it_count_favs(request)})


    def post(self, request, *args, **kwargs):
        """
        Delete several Favs at a time
        set date_deleted = now
        """
        for fav_id in self.request.POST.getlist('favs[]'):
            favs = get_favs(request)
            favs = favs.filter(itinerary__pk=fav_id)
            if favs.exists():
                for fav in favs.all():
                    fav.date_deleted = datetime.today()
                    fav.save()
        return Response({'status':'ok', 'count': get_favs_count(request), 'count_it' : get_it_count_favs(request)})

class AddOperatorFavAPIView(APIView):

    def get(self, request, operator_pk):
        """
        Create a Fav
        TODO
        """
        counts = get_favs_count(request)
        if counts >= 10:
            return Response({'status':'error', 'message': 'You cannot add more than 10 items to your shortlists'})
        from django.shortcuts import get_object_or_404
        fav = Fav()
        if self.request.user.is_authenticated:
            fav.user = self.request.user
        else:
            if not 'uuid' in request.session: 
                request.session['uuid'] = str(uuid.uuid1())
            fav.uuid = request.session['uuid']
        fav.tour_operator = get_object_or_404(TourOperator,  pk = operator_pk)
        fav.save()
        return Response({'status':'ok', 'count': get_favs_count(request)})
        
class DeleteOperatorFavAPIView(APIView):

    def get(self, request, *args, **kwargs):
        """
        Delete a Fav
        set date_deleted = now
        """
        favs = get_favs(request)
        favs = favs.filter(tour_operator__pk=self.kwargs.get('operator_pk'))
        if favs.exists():
            for fav in favs.all():
                fav.date_deleted = datetime.today()
                fav.save()
        return Response({'status':'ok', 'count': get_favs_count(request), 'count_to' : get_to_favs_count(request)})


    def post(self, request, *args, **kwargs):
        """
        Delete several Favs at a time
        set date_deleted = now
        """
        for fav_id in self.request.POST.getlist('favs[]'): 
            favs = get_favs(self.request)
            favs = favs.filter(tour_operator__pk=fav_id)
            if favs.exists():
                for fav in favs.all():
                    fav.date_deleted = datetime.today()
                    fav.save()
        return Response({'status':'ok', 'count': get_favs_count(request), 'count_to' : get_to_favs_count(request)})