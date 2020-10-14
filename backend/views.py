from itertools import chain
from smtplib import SMTPException
from django.conf import settings
from .forms import TourOperatorReviewForm, ParkReviewForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from reviews.models import ParkReview,TourOperatorReview,AbstractReview
from analytics.models import Analytic
from post_office.models import EmailTemplate
from blog.models import Article
from django.shortcuts import render
from django.views.generic import TemplateView, UpdateView
from django.views import View
from operators.models import TourOperator, QuoteRequest
from users.models import UserProfile
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from operators.models import Itinerary, Itinerary
from operators.models import Month, ItineraryInclusion, ItineraryExclusion
from photos.models import Photo
from backend.controllers.VisitCount import VisitCount
from datetime import datetime, timedelta
from backend.forms import CompanyInfoForm, TourPackageForm, MemberInfoProfileForm, MemberInfoUserForm
from places.models import CountryIndex, Park, Country, Language, Animal, Activity
from places.models import Currency
from django.contrib import messages
from backend.forms import TourOperatorFilterForm
from operators.models import ItineraryType, ItineraryDayDescription
import requests
from core.models import EmailLog
from yas.settings import BASE_URL
from photos.photos_json import photo_to_json
from reviews.models import ParkReview, TourOperatorReview
import json
from post_office import mail
from .forms import TestEmailForm, EmailTemplateForm
from django.shortcuts import redirect
from backend.forms import CompanyInfoForm, TourPackageForm
from places.models import CountryIndex, Park, Country, Activity
from places.models import Currency
from django.contrib import messages
from backend.forms import TourOperatorFilterForm
from operators.models import ItineraryType, ItineraryDayDescription
from core.utils import formatted_decimal_plain
from django.template.defaultfilters import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import os
from backend.forms import YASScoreForm, QuoteRequestFilterForm
from django.db.models import Q
from django.utils import timezone
from django.db.models import Count, Sum
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.decorators import method_decorator
from backend.inc_views.admin import *

class TourOperatorRequiredLoginView(UserPassesTestMixin, LoginRequiredMixin):

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.profile.is_tour_operator()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['operator'] = self.request.user.profile.tour_operator
        return context


class MemberRequiredLoginView(UserPassesTestMixin, LoginRequiredMixin):

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def photos_for_edit(self, context, tour_operator=None):
    page = self.request.GET.urlencode()
    if page:
        page = int(page.split('=')[1])
    else:
        page = 1
    user = self.request.user
    photo_api_request = requests.post(self.request.build_absolute_uri(reverse('photos:api_photos')),
                                      data={'username': user.username})

    if tour_operator:
        photos = Photo.objects.filter(draft=False, date_deleted__isnull=True, tour_operator=tour_operator)
    else:
        photos = Photo.objects.filter(draft=False, date_deleted__isnull=True, user=user)
    response = photo_api_request.json()
    if 'photos_json' in response:
        context['photos_json'] = response['photos_json']

    limit_1 = ((page - 1) * 21)
    limit_2 = limit_1 + 21
    response = {}
    photos_response = photo_to_json(self.request, response, photos, limit_1, limit_2)

    context['photos_json'] = photos_response['photos_json']
    context['photos_count'] = response['photos_count']
    context['page_count'] = response['page_count']
    return context


class BackendMemberRequiredLoginView(MemberRequiredLoginView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['disable_footer'] = True
        return context


class BackendTourOperatorRequiredLoginView(UserPassesTestMixin, LoginRequiredMixin):

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.profile.is_tour_operator()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['disable_footer'] = True
        new_quote_requests = QuoteRequest.objects.all()
        new_quote_requests = new_quote_requests.filter(
            tour_operator=self.request.user.profile.tour_operator)
        new_quote_requests = new_quote_requests.filter(
            status=QuoteRequest.STATUS_PENDING)
        context['new_quote_requests'] = new_quote_requests.count()
        context['operator'] = self.request.user.profile.tour_operator
        context['new_pending_reviews'] = TourOperatorReview.objects.filter(
            tour_operator=self.request.user.profile.tour_operator, status=TourOperatorReview.PENDING).count()
        context['number_tour_packages'] = Itinerary.objects.filter(
            tour_operator=self.request.user.profile.tour_operator, date_deleted__isnull=True).count()

        return context


class MemberProfileView(BackendMemberRequiredLoginView, TemplateView):
    template_name = "backend/member/my_profile.html"

    def post(self, request, *args, **kwargs):

        if request.POST.getlist('user_type'):
            user_type = request.POST.getlist('user_type')
            if len(user_type) == 1:
                request.user.profile.user_type = user_type[0]

        if request.POST.get('luxury_level'):
            luxury_level = request.POST.getlist('luxury_level')
            if len(luxury_level) == 1:
                request.user.profile.luxury_level = luxury_level[0]

        request.user.profile.countries_visited.clear()
        if request.POST.get('countries_visited'):
            countries_ids = [int(country) for country in request.POST.getlist('countries_visited')]
            countries_objects = CountryIndex.objects.filter(id__in=countries_ids)
            request.user.profile.countries_visited.add(*countries_objects)

        request.user.profile.animals_seen.clear()
        if request.POST.getlist('animals'):
            animals_ids = [int(animal) for animal in request.POST.getlist('animals')]
            animals_objects = Animal.objects.filter(id__in=animals_ids)
            request.user.profile.animals_seen.add(*animals_objects)

        request.user.profile.activities_enjoy.clear()
        if request.POST.getlist('activities_safari'):
            activities_safari_ids = [int(activity) for activity in request.POST.getlist('activities_safari')]
            activities_safari_objects = Activity.objects.filter(id__in=activities_safari_ids)
            request.user.profile.activities_enjoy.add(*activities_safari_objects)

        if request.POST.getlist('activities_non_safari'):
            activities_non_safari_ids = [int(activity) for activity in request.POST.getlist('activities_non_safari')]
            activities_non_safari_objects = Activity.objects.filter(id__in=activities_non_safari_ids)
            request.user.profile.activities_enjoy.add(*activities_non_safari_objects)

        form1 = MemberInfoProfileForm(self.request.POST or None, instance=self.request.user.profile)
        form2 = MemberInfoUserForm(self.request.POST or None, instance=self.request.user,
                                   initial={'groups': self.request.user.groups})
        if form1.is_valid():
            form1.save()
            if form2.is_valid():
                instance = form2.save(commit=False)
                instance.groups.set(self.request.user.groups.all())
                instance.save()
            messages.success(self.request, 'Profile data updated')
            return self.render_to_response(self.get_context_data())
        else:
            messages.error(self.request, form1.errors)
            messages.error(self.request, form2.errors)
            return self.render_to_response(self.get_context_data(form=form1))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # About:
        user = self.request.user
        context['profile'] = user.profile
        context['user_types'] = UserProfile.USER_TYPE_CHOICES

        context['countries_visited'] = CountryIndex.objects.all().order_by('name')
        context['animals'] = Animal.objects.all().order_by('name')
        context['activities_safari'] = Activity.objects.filter(activity_type="SAFARI").order_by('name')
        context['activities_non_safari'] = Activity.objects.filter(activity_type="NON_SAFARI").order_by('name')
        if user.profile.avatar:
            context['avatar'] = user.profile.avatar.url
        else:
            context['avatar'] = ''

        context['display_name'] = 'Edit member profile'
        context['form1'] = MemberInfoProfileForm(instance=user.profile)
        context['form2'] = MemberInfoUserForm(instance=user)
        countries = CountryIndex.objects.all().order_by('name')
        context['countries'] = countries
        parks = Park.objects.all().order_by('name')
        context['parks'] = parks

        countries_json = []
        for country in countries:
            country_json = {}
            country_json['id'] = country.id
            country_json['name'] = country.name
            country_json['parks'] = list(country.parks.all().values('id', 'name'))
            countries_json.append(country_json)
        context['vue_variables'] = {}
        context['vue_variables']['countries_json'] = countries_json

        LODGE_OWNER = "LO"
        NON_PROFIT = "NP"
        SAFARI_GUIDE = "SG"
        SAFARI_ENTHUSIAST = "SE"
        SAFARI_TOUR_OPERATOR = "TO"
        TRAVEL = "TA"
        TRAVEL_WRITE = "TW"

        context['types_dict'] = {
            LODGE_OWNER: "I own, manage or work at a safari lodge/camp",
            NON_PROFIT: "I work for or own a non-profit company, such as African Wildlife Federation",
            SAFARI_GUIDE: "I work as a safari guide or driver, either independently or for a tour operator",
            SAFARI_ENTHUSIAST: "I have been on safari or am looking to go on safari",
            SAFARI_TOUR_OPERATOR: "I own or work for a safari company that offers tours in Africa",
            TRAVEL: "I work for or own a travel agency",
            TRAVEL_WRITE: "I am a travel writer/blogger/Tweeter",
        }

        return context


class MemberPhotosView(BackendMemberRequiredLoginView, TemplateView):
    template_name = "backend/member/my_photos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = photos_for_edit(self, context)
        context['is_tour_operator'] = False
        return context


class MemberReviewsView(BackendMemberRequiredLoginView, TemplateView):
    template_name = "backend/member/my_reviews.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        touroperator_reviews = TourOperatorReview.objects.filter(user=user, status__in=['AC', 'PE'])
        park_reviews = ParkReview.objects.filter(user=user, status__in=['AC', 'PE'])
        context['reviews'] = list(chain(park_reviews, touroperator_reviews))
        return context


# ADMIN


class AdminTourOperatorYasScoreView(AdminRequiredLoginView, TemplateView):
    template_name = "backend/admin/yas_score.html"

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = YASScoreForm(self.request.POST)
        context['form'] = form
        if form.is_valid():
            country = form.cleaned_data['country']
            context['operator'].yas_score_temp_country = country
            context['country'] = country
        return self.render_to_response(context)

    def get_context_data(self, pk, **kwargs):
        context = super().get_context_data(**kwargs)
        context['operator'] = TourOperator.objects.get(pk=self.kwargs.get('pk'))
        context['form'] = YASScoreForm()
        return context


class AdminEmailTemplatesEditView(AdminRequiredLoginView, TemplateView):
    template_name = "backend/admin/email_templates_edit.html"

    def post(self, request, *args, **kwargs):
        template = EmailTemplate.objects.get(pk=self.kwargs.get('pk'))
        form = EmailTemplateForm(self.request.POST or None, instance=template)
        if form.is_valid():
            form.save()
            messages.success(self.request, 'Email template updated')
            return redirect('backend:admin_email_templates')
        else:
            messages.error(self.request, 'There was an error with your submission {}'.format(form.errors))
            return self.render_to_response(self.get_context_data(form=form))


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        template = EmailTemplate.objects.get(pk=self.kwargs.get('pk'))
        if self.kwargs.get('form'):
            context['form'] = self.kwargs.get('form')
        else:
            context['form'] = EmailTemplateForm(instance=template)
        return context



class AdminEmailTemplatesOpenView(AdminRequiredLoginView, TemplateView):
    template_name = "backend/admin/email_template_open.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['template'] = EmailTemplate.objects.get(pk=self.kwargs.get('pk'))
        return context

class AdminEmailTemplatesView(AdminRequiredLoginView, TemplateView):
    template_name = "backend/admin/email_templates.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['templates'] = EmailTemplate.objects.all()
        return context



class AdminTestEmailView(AdminRequiredLoginView, TemplateView):
    template_name = "backend/admin/test_email.html"

    def post(self, request, *args, **kwargs):
        form = TestEmailForm(self.request.POST or None)
        if form.is_valid():
            template = form.cleaned_data['template']
            log_entry = EmailLog()
            log_entry.address_to = form.cleaned_data['email_to']
            log_entry.address_from = 'Your African Safari <support@yourafricansafari.com>'
            log_entry.subject = template.subject
            log_entry.body = template.html_content
            log_entry.save()
            mail.send(
                form.cleaned_data['email_to'],
                'Your African Safari <support@yourafricansafari.com>',
                subject=template.subject,
                html_message=template.html_content,
                priority='now'
            )
            messages.success(self.request, 'Email sent')
            return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['display_name'] = 'Test E-mails'
        context['form'] = TestEmailForm()
        return context


class AdminArticlesView(AdminRequiredLoginView, TemplateView):
    template_name = "backend/admin/articles.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # sort
        articles = Article.objects.all().order_by('pk')

        # page logic
        page = self.request.GET.get('page', 1)
        paginator = Paginator(articles, 10)
        try:
            context['articles'] = paginator.page(page)
        except PageNotAnInteger:
            context['articles'] = paginator.page(1)
        except EmptyPage:
            context['articles'] = paginator.page(paginator.num_pages)
        return context


class AdminDashboardView(AdminRequiredLoginView, TemplateView):
    template_name = "backend/admin/index.html"

    def send_tour_operator_welcome_email(self, tour_operator):
        email_to = tour_operator.email
        if not settings.REAL_EMAILS:
            email_to = settings.TESTING_EMAILS
        from post_office import mail
        URL = settings.BASE_URL
        
        tour_operator_edit_profile_path = reverse('backend:tour_operator_profile')
        tour_operator_edit_profile_link = URL +  tour_operator_edit_profile_path
        
        tour_operator_listing_path = reverse('all_tour_packages_operator', kwargs={'operator':tour_operator.slug})
        tour_operator_listing_link = URL +  tour_operator_listing_path
        
        context = {'tour_operator': tour_operator.name,
                    'link_tp': tour_operator_listing_link,
                    'link':tour_operator_edit_profile_link}
        mail.send(
            email_to,
            'Your African Safari <support@yourafricansafari.com>',
            template='tour_operator_added_YAS',
            context=context,
        )
    

    def send_tour_operator_reject_email(self, tour_operator):
        email_to = tour_operator.email
        if not settings.REAL_EMAILS:
            email_to = settings.TESTING_EMAILS
        from post_office import mail
        URL = settings.BASE_URL
        context = {'tour_operator': tour_operator.name}
        mail.send(
            email_to,
            'Your African Safari <support@yourafricansafari.com>',
            template='tour_operator_rejected',
            context=context,
        )
    

    def approve_tour_operator(self, pk):
        to = TourOperator.objects.get(pk=pk)
        to.draft = False
        to.save()
        to.user.profile.tour_operator = to
        to.user.profile.save()
        self.send_tour_operator_welcome_email(to)
        messages.success(self.request, 'Tour operator approved')

    def reject_tour_operator(self, pk):
        to = TourOperator.objects.get(pk=pk)
        to.date_deleted = datetime.today()
        to.save()
        self.send_tour_operator_reject_email(to)
        messages.success(self.request, 'Tour operator rejected')


    def get(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        if self.request.GET.get('approve_tour_operator'):
            self.approve_tour_operator(self.request.GET.get('approve_tour_operator'))
            return redirect('backend:admin')
        if self.request.GET.get('reject_tour_operator'):
            self.reject_tour_operator(self.request.GET.get('reject_tour_operator'))
            return redirect('backend:admin')
        if self.request.GET.get('delete_park_review'):
            review = ParkReview.objects.get(pk=self.request.GET.get('delete_park_review'))
            review.date_deleted = timezone.now()
            review.save()
            messages.success(self.request, 'Review deleted')
            return redirect('backend:admin')
        if self.request.GET.get('delete_tour_operator'):
            review = TourOperatorReview.objects.get(pk=self.request.GET.get('delete_tour_operator'))
            review.date_deleted = timezone.now()
            review.save()
            messages.success(self.request, 'Review deleted')
            return redirect('backend:admin')

        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        park_reviews = ParkReview.objects.filter(date_deleted__isnull=True).filter(status=AbstractReview.PENDING).order_by('-date_created')
        tour_operator_reviews = TourOperatorReview.objects.filter(date_deleted__isnull=True).filter(status=AbstractReview.PENDING).order_by('-date_created')
        from itertools import chain
        reviews = chain(park_reviews, tour_operator_reviews)
        context['reviews'] = sorted(reviews, key=lambda obj: obj.date_created, reverse=True)
        context['pending_tour_operator'] = TourOperator.objects.filter(draft=True).filter(date_deleted__isnull=True)
        
        return context


class AdminOpenTourOperatorView(AdminRequiredLoginView, TemplateView):
    template_name = "backend/admin/open_tour_operator.html"

    def post(self, request, **kwargs):
        if self.kwargs.get('park_review_pk'):
            review = ParkReview.objects.get(pk=self.kwargs.get('park_review_pk'))
            form = ParkReviewForm(request.POST,instance=review)
        if self.kwargs.get('tour_operator_review_pk'):
            review = TourOperatorReview.objects.get(pk=self.kwargs.get('tour_operator_review_pk'))
            form = TourOperatorReviewForm(request.POST, instance=review)
        if not form.is_valid():
            messages.success(self.request, 'Please review the errors in the form')    
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)
        review = form.save()
        review.date_modified = datetime.today()
        review.save()
        if review.status == AbstractReview.ACTIVE:
            self.send_review_approve_email(review)
            if review.is_tour_operator_review():
                self.send_review_tour_operator_email(review)
        if review.status == AbstractReview.REJECTED:
            self.send_review_reject_email(review)
        messages.success(self.request, 'Review updated')
        return redirect('backend:admin')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tour_operator = TourOperator.objects.get(pk=self.kwargs.get('pk'))
        context['form'] = CompanyInfoForm(instance=tour_operator)
        context['tour_operator'] = tour_operator        
        return context


class AdminOpenReviewView(AdminRequiredLoginView, TemplateView):
    template_name = "backend/admin/open_review.html"
    
    def send_review_tour_operator_email(self, review):
        email_to = review.user.email
        if not settings.REAL_EMAILS:
            email_to = settings.TESTING_EMAILS
        from post_office import mail
        
        URL = settings.BASE_URL
        path = reverse('tour_operator_review', kwargs={'review': review.id, 'slug': review.tour_operator.slug})
        link = URL + path
        
        tour_operator_edit_profile_path = reverse('backend:tour_operator_profile')
        tour_operator_edit_profile_link = URL +  tour_operator_edit_profile_path

        mail.send(
            email_to,
            'Your African Safari <support@yourafricansafari.com>',
            template='review_notify_tour_operator',
            context={'tour_operator': review.tour_operator.name,
                    'link': link,
                    'tour_operator_edit_profile_link':tour_operator_edit_profile_link},
        )
    
    def send_review_reject_email(self, review):
        email_to = review.user.email
        if not settings.REAL_EMAILS:
            email_to = settings.TESTING_EMAILS
        from post_office import mail
        URL = settings.BASE_URL
        path = reverse('reviews:create')
        link = URL + path
        if type(review) == type(ParkReview()):
            reviewed = review.park
        if type(review) == type(TourOperatorReview()):
            reviewed = review.tour_operator
        if review.reject_reason:
            reason = review.reject_reason
        else:
            reason = ''
        context = {
            'reviewed': reviewed,
            'member': review.user.profile.display_name_for_email(),
            'reason': reason,
            'link': link,
        }
        mail.send(
            email_to,
            'Your African Safari <support@yourafricansafari.com>',
            template='review_rejected',
            context=context,
        )
        
    def send_review_approve_email(self, review):
        email_to = review.user.email
        if not settings.REAL_EMAILS:
            email_to = settings.TESTING_EMAILS
        from post_office import mail
        
        URL = settings.BASE_URL
        if type(review) == type(ParkReview()):
            path = reverse('park_review', kwargs={'review_pk': review.id,'slug': review.park.slug})
            link = URL + path
        if type(review) == type(TourOperatorReview()):
            path = reverse('tour_operator_review', kwargs={'review': review.id, 'slug': review.tour_operator.slug})
            link = URL + path
        context = {
            'member': review.user.profile.display_name_for_email(),
            'link': link,
        }
        mail.send(
            email_to,
            'Your African Safari <support@yourafricansafari.com>',
            template='review_approved',
            context=context,
        )
    

    def post(self, request, **kwargs):
        if self.kwargs.get('park_review_pk'):
            review = ParkReview.objects.get(pk=self.kwargs.get('park_review_pk'))
            form = ParkReviewForm(request.POST,instance=review)
        if self.kwargs.get('tour_operator_review_pk'):
            review = TourOperatorReview.objects.get(pk=self.kwargs.get('tour_operator_review_pk'))
            form = TourOperatorReviewForm(request.POST, instance=review)
        if not form.is_valid():
            messages.success(self.request, 'Please review the errors in the form')    
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)
        review = form.save()
        review.date_modified = datetime.today()
        review.save()
        if review.status == AbstractReview.ACTIVE:
            self.send_review_approve_email(review)
            if review.is_tour_operator_review():
                self.send_review_tour_operator_email(review)
        if review.status == AbstractReview.REJECTED:
            self.send_review_reject_email(review)
        messages.success(self.request, 'Review updated')
        return redirect('backend:admin')

    def get_context_data(self, **kwargs):
        from django.template.loader import get_template

        context = super().get_context_data(**kwargs)
        if self.kwargs.get('park_review_pk') and not 'form' in context:
            review = ParkReview.objects.get(pk=self.kwargs.get('park_review_pk'))
            context['form'] = ParkReviewForm(instance=review)
            context['what'] = review.park
            context['title'] = 'Park'
            temp = get_template('places/park_inserts/park_reviews.html')
            result = temp.render({'reviews': [review], 'focused': True})
            context['review_focus'] = result


        if self.kwargs.get('tour_operator_review_pk') and not 'form' in context:
            review = TourOperatorReview.objects.get(pk=self.kwargs.get('tour_operator_review_pk'))
            context['form'] = TourOperatorReviewForm(instance=review)
            context['what'] = review.tour_operator
            context['title'] = 'Tour operator'
            
            temp = get_template('operators/tour_operator_includes/tour_reviews_cards.html')
            result = temp.render({'tour_reviews': [review], 'tour': review.tour_operator, 'focused': True})
            context['review_focus'] = result
        context['review'] = review
        return context


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import ArticleForm
class AdminArticleChangeView(AdminRequiredLoginView, TemplateView):
    template_name = "backend/admin/article.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = Article.objects.get(slug=self.kwargs.get('slug'))
        form = ArticleForm(instance=article)
        context['form'] = form
        return context





class AdminQuoteRequestView(AdminRequiredLoginView, TemplateView):
    template_name = "backend/admin/quote_requests.html"

    def get(self, request, *args, **kwargs):
        form = QuoteRequestFilterForm(self.request.GET or None)
        if form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))
        else:
            return self.render_to_response(self.get_context_data())
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # is form sent?
        if 'form' in kwargs and kwargs['form']:
            context['form'] = kwargs['form']
        else:
            context['form'] = QuoteRequestFilterForm()
        objs = QuoteRequest.objects.all()
        # filter logic
        if 'form' in kwargs and kwargs['form']:
            tour_operator = kwargs['form'].cleaned_data.get('tour_operator')
            if tour_operator:
                objs = objs.filter(tour_operator=tour_operator)
            country_index = kwargs['form'].cleaned_data.get('country_index')
            if country_index:
                objs = objs.filter(country_indexes=country_index)
            date_range = kwargs['form'].cleaned_data.get('date_range')
            if date_range:
                date_from = date_range.split('-')[0].strip()
                date_to = date_range.split('-')[1].strip()
                date_from = datetime.strptime(date_from, '%d/%m/%Y')
                date_to = datetime.strptime(date_to, '%d/%m/%Y')
                objs = objs.filter(date_created__range=(date_from, date_to))
            only_unseen = kwargs['form'].cleaned_data.get('only_unseen')
            if only_unseen:
                objs = objs.filter(seen=False)
            
        
        objs = objs.order_by('-date_created')        
        # page logic
        page = self.request.GET.get('page', 1)
        paginator = Paginator(objs, 100)
        try:
            context['paginator'] = paginator.page(page)
        except PageNotAnInteger:
            context['paginator'] = paginator.page(1)
        except EmptyPage:
            context['paginator'] = paginator.page(paginator.num_pages)
        #context['sort'] = sort
        #context['how'] = how
        return context


class TourOperatorDashboardView(BackendTourOperatorRequiredLoginView, TemplateView):
    template_name = "backend/tour_operator/dashboard.html"

    def test_func(self):
        return self.request.user.profile.is_tour_operator()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['display_name'] = 'Dashboard'

        top_packages = Itinerary.objects.all()
        top_packages = top_packages.filter(tour_operator=self.request.user.profile.tour_operator)
        top_packages = top_packages.order_by('-visit_count')
        top_package = top_packages.first()
        context['top_package'] = top_package

        top_photos = Photo.objects.all()
        top_photos = top_photos.filter(tour_operator=self.request.user.profile.tour_operator)
        top_photos = top_photos.order_by('-visit_count')
        top_photo = top_photos.first()
        context['top_photo'] = top_photo

        visit_count = VisitCount(self.request.user.profile.tour_operator)
        context['visit_count'] = visit_count.weekly()

        # world map
        date_from = datetime.today() - timedelta(days=117)
        date_to = datetime.today()
        context['worldmap'] = visit_count.worldmap(date_from, date_to)

        context['worldtable'] = visit_count.worldtable(date_from, date_to)

        context['tour_operator'] = self.request.user.profile.tour_operator
        return context

class TourOperatorWidgetsView(BackendTourOperatorRequiredLoginView, TemplateView):
    template_name = "backend/tour_operator/widgets.html"

    def test_func(self):
        return self.request.user.profile.is_tour_operator()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tour_operator'] = self.request.user.profile.tour_operator
        context['display_name'] = 'YAS Widgets'
        context['reviews'] = TourOperatorReview.objects.filter(tour_operator=self.request.user.profile.tour_operator)[:3]
        context['page_url'] = BASE_URL
        return context


class TourOperatorAdvertiseView(BackendTourOperatorRequiredLoginView, TemplateView):
    template_name = "backend/tour_operator/advertise.html"

    def test_func(self):
        return self.request.user.profile.is_tour_operator()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TourOperatorAnalyticsView(BackendTourOperatorRequiredLoginView, TemplateView):
    template_name = "backend/tour_operator/analytics.html"

    def post(self, request, **kwargs):
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['display_name'] = 'Analytics'
        if self.request.POST:
            context['date_range'] = self.request.POST.get('date_range')
        else:
            date_to = datetime.now()
            date_from = date_to.__add__(timedelta(days=-14))
            context['date_range'] = '{} - {}'.format(date_from.strftime("%d/%m/%Y"), date_to.strftime('%d/%m/%Y'))

        
        # data
        tour_operator = self.request.user.profile.tour_operator

        # visits logic
        visits_counts = VisitCount(tour_operator)
        date_from = context['date_range'].split('-')[0].strip()
        date_to = context['date_range'].split('-')[1].strip()
        date_from = datetime.strptime(date_from, '%d/%m/%Y')
        date_to = datetime.strptime(date_to, '%d/%m/%Y')
        visits = visits_counts.visits_date_daily(date_from, date_to)
        context['vue_variables'] = {}
        context['vue_variables']['labels'] = visits['labels']
        context['vue_variables']['series'] = visits['series']

        # other data:

        # 5 most read reviews:
        top_reviews = TourOperatorReview.objects.filter(tour_operator=tour_operator).order_by('-kudu_count')[:5]

        # 5 top packages:
        top_packages = Itinerary.objects.filter(tour_operator=tour_operator).order_by('-visit_count')[:5]

        # worldtable:
        worldtable = visits_counts.worldtable(date_from, date_to)
        wordltable_sorted = sorted(worldtable.items(), key=lambda x: x[1][1],
                                   reverse=True)

        # worldmap:
        context['worldmap'] = visits_counts.worldmap(date_from, date_to)

        context['worldtable'] = wordltable_sorted
        context['top_country'] = ''
        if wordltable_sorted:
            context['top_country'] = wordltable_sorted[0]
        context['top_review'] = top_reviews.first()
        context['top_package'] = top_packages.first()
        context['top_reviews'] = top_reviews
        context['top_packages'] = top_packages

        return context

class TourOperatorClientReviewView(BackendTourOperatorRequiredLoginView, TemplateView):
    template_name = "backend/tour_operator/client_review.html"


    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['display_name'] = 'Client reviews'
        page = self.request.GET.get('page', 1)
        tour_operator = self.request.user.profile.tour_operator
        context['to'] = tour_operator
        total_tour_operator_reviews = TourOperatorReview.objects.filter(tour_operator=tour_operator,status=TourOperatorReview.ACTIVE).order_by('-date_created').count()
        context['total_tour_operator_reviews'] = total_tour_operator_reviews
        tour_operator_reviews = TourOperatorReview.objects.all().order_by('-date_created')
        paginator = Paginator(tour_operator_reviews, 10)
        try:
            context['paginator'] = paginator.page(page)
        except PageNotAnInteger:
            context['paginator'] = paginator.page(1)
        except EmptyPage:
            context['paginator'] = paginator.page(paginator.num_pages)
        return context

    def post(self, request, *args, **kwargs):
        review_id = int(request.POST['review_id'])
        response = request.POST['response']
        review = TourOperatorReview.objects.get(id=review_id)
        if not review.response:
            review.response = response
            review.response_date = datetime.now()
            review.save()

        to_email = review.user.email
        context = {}
        context['tour_operator'] = review.tour_operator.name
        context['review_title'] = review.title
        from django.conf import settings
        context['link'] = settings.BASE_URL + reverse('tour_operator_review',
                                                     kwargs={'slug': review.tour_operator.slug, 'review': review.pk})
        if not settings.REAL_EMAILS:
            to_email = settings.TESTING_EMAILS
        try:
            res = mail.send(
                to_email,
                'Your African Safari <support@yourafricansafari.com>',
                template='review_tour_operator_responded',
                context=context,
            )
            messages.success(self.request, 'The response has been sent')
        except SMTPException as e:
            messages.error(self.request, 'An unexpected error has occurred. Please try again later.')
        return redirect('backend:tour_operator_client_review')


class TourOperatorEditProfileView(BackendTourOperatorRequiredLoginView, TemplateView):
    template_name = "backend/tour_operator/edit_profile.html"
    form_class = CompanyInfoForm
    model = TourOperator

    def post(self, request, *args, **kwargs):
        operator = self.request.user.profile.tour_operator

        form = CompanyInfoForm(self.request.POST or None, instance=self.request.user.profile.tour_operator)
        if form.is_valid():
            instance = form.save(commit=False)
            form.save()
            form.save_m2m()
            messages.success(self.request, 'Profile updated')
            return self.render_to_response(self.get_context_data(form=form))
        else:
            messages.error(self.request, form.errors)
            return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['display_name'] = 'Edit company profile'
        context['tour_operator'] = self.request.user.profile.tour_operator
        context['form'] = CompanyInfoForm(instance=self.request.user.profile.tour_operator)
        countries = CountryIndex.objects.all().order_by('name').prefetch_related('parks')
        context['countries'] = countries
        parks = Park.objects.all().order_by('name')
        context['parks'] = parks

        countries_json = []
        for country in countries:
            country_json = {}
            country_json['id'] = country.id
            country_json['name'] = country.name
            country_json['parks'] = list(country.parks.all().order_by('name').values_list('id', flat=True))
            countries_json.append(country_json)
        context['vue_variables'] = {}
        context['vue_variables']['countries_json'] = countries_json

        countries = CountryIndex.objects.all().order_by('name')
        context['countries'] = countries
        parks = Park.objects.all().order_by('name')
        context['parks'] = parks
        parks_json = []
        for park in parks:
            park_json = {}
            park_json['id'] = park.id
            park_json['name'] = park.name_short
            parks_json.append(park_json)
        context['vue_variables']['parks_json'] = parks_json
        return context


class TourOperatorRemovePackagesView(BackendTourOperatorRequiredLoginView, View):

    def get(self, request, *args, **kwargs):
        itinerary = Itinerary.objects.filter(pk=self.kwargs.get('pk'))
        itinerary = itinerary.filter(tour_operator=self.request.user.profile.tour_operator)
        if not itinerary.exists():
            messages.error(self.request, 'Not a valid tour package')
            response = redirect('backend:tour_operator_packages')
            return response
        itinerary = itinerary.first()
        itinerary.date_deleted = datetime.today()
        itinerary.save()
        messages.success(self.request, 'Tour package removed succesfully')
        return redirect('backend:tour_operator_packages')


class TourOperatorPhotosView(BackendTourOperatorRequiredLoginView, TemplateView):
    template_name = "backend"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tour_operator = self.request.user.profile.tour_operator
        context = photos_for_edit(self, context, tour_operator)
        context['is_tour_operator'] = True
        return context


class TourOperatorQuoteRequestsView(BackendTourOperatorRequiredLoginView, TemplateView):
    template_name = "backend/tour_operator/quote_requests.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['display_name'] = 'Quote requests'
        tour_operator = self.request.user.profile.tour_operator

        quote_requests = QuoteRequest.objects.filter(
            Q(tour_operator=tour_operator) | Q(itinerary__tour_operator=tour_operator)).order_by('-date_created')

        context['quote_requests'] = quote_requests
        return context


class TourOperatorPackagesView(BackendTourOperatorRequiredLoginView, TemplateView):
    template_name = "backend/tour_operator/tour_packages.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        itineraries = Itinerary.objects.filter(tour_operator=self.request.user.profile.tour_operator)
        itineraries = itineraries.filter(date_deleted=None)
        context['itineraries'] = itineraries.order_by('-pk')
        return context


class TourOperatorPackagePhotosView(BackendTourOperatorRequiredLoginView, TemplateView):
    template_name = "backend/tour_operator/tour_packages_photos.html"

    def get_context_data(self, slug, **kwargs):
        context = super().get_context_data(**kwargs)
        itineraries = Itinerary.objects.filter(tour_operator=self.request.user.profile.tour_operator)
        itineraries = itineraries.filter(date_deleted=None)
        itineraries = itineraries.filter(slug=slug)
        itinerary = itineraries.first()
        context['itinerary'] = itinerary
        page = self.request.GET.get('page', 1)
        user = self.request.user
        profile = user.profile
        photos = Photo.objects.filter(draft=False, date_deleted__isnull=True, itinerary__slug=slug)
        limit_1 = ((page - 1) * 21)
        limit_2 = limit_1 + 21
        response = {}
        photos_response = photo_to_json(self.request, response, photos, limit_1, limit_2)
        context['photos_json'] = photos_response['photos_json']
        context['photos_count'] = photos_response['photos_count']
        context['page_count'] = photos_response['page_count']
        return context


class TourOperatorAddPackagesView(BackendTourOperatorRequiredLoginView, TemplateView):
    template_name = "backend/tour_operator/add_tour_package.html"
    form_class = TourPackageForm
    model = Itinerary

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        # create the form
        if 'itinerary' in context:
            itinerary = context['itinerary']
            itinerary.date_modified = datetime.today()
        else:
            itinerary = Itinerary()
            itinerary.tour_operator = self.request.user.profile.tour_operator
        import bleach
        data = self.request.POST
        # set the data manually
        itinerary.title = bleach.clean(data.get('title'))
        itinerary.needs_update = False
        # itinerary.header = bleach.clean(data.get('header'))
        itinerary.summary = bleach.clean(data.get('summary', ''))
        itinerary.title_short = bleach.clean(data.get('title_short', ''))
        itinerary.itinerary_type = ItineraryType.objects.get(pk=data.get('itinerary_type')[0])

        itinerary.safari_focus_activity = Activity.objects.get(pk=data.get('safari_focus_activity'))

        # we need to save it for the many2many pk
        itinerary.save()
        itinerary.slug = slugify("{}-{}".format(itinerary.pk, data.get('title')))
        itinerary.accept_terms = True
        itinerary.save()

        # secondary focus
        secondary_focus_pks = data.getlist('secondary_focus_activity')
        secondary_focuses = []
        for secondary_focus_pk in secondary_focus_pks:
            secondary_focus = Activity.objects.get(pk=secondary_focus_pk)
            secondary_focuses.append(secondary_focus)
        itinerary.secondary_focus_activity.set(secondary_focuses)

        # country_indexes
        country_index_pks = data.getlist('country_indexes')
        country_indexes = []
        for country_index_pk in country_index_pks:
            country_index = CountryIndex.objects.get(pk=country_index_pk)
            country_indexes.append(country_index)
        itinerary.country_indexes.set(country_indexes)

        # parks
        parks_pks = data.getlist('parks')
        parkses = []
        for parks_pk in parks_pks:
            parks = Park.objects.get(pk=parks_pk)
            parkses.append(parks)
        itinerary.parks.set(parkses)

        # months
        months_pks = data.getlist('months')
        months = []
        for months_pk in months_pks:
            month = Month.objects.get(pk=months_pk)
            months.append(month)
        itinerary.months.set(months)

        # inclusions
        inclusions_pks = data.getlist('inclusions')
        inclusions = []
        for inclusions_pk in inclusions_pks:
            inclusion = ItineraryInclusion.objects.get(pk=inclusions_pk)
            inclusions.append(inclusion)
        itinerary.inclusions.set(inclusions)
        if data.get('other_inclusion') == 'on':
            itinerary.other_inclusion = True
            itinerary.other_inclusion_text = data.get('other_inclusion_text')
        else:
            itinerary.other_inclusion = False

        # exclusion
        exclusions_pks = data.getlist('exclusions')
        exclusions = []
        for exclusions_pk in exclusions_pks:
            exclusion = ItineraryExclusion.objects.get(pk=exclusions_pk)
            exclusions.append(exclusion)
        itinerary.exclusions.set(exclusions)
        if data.get('other_exclusion') == 'on':
            itinerary.other_exclusion = True
            itinerary.other_exclusion_text = data.get('other_exclusion_text')
        else:
            itinerary.other_exclusion = False

        # currency
        itinerary.currency = Currency.objects.get(pk=data.get('currency')[0])

        # price
        itinerary.min_price = formatted_decimal_plain(data.get('min_price'))
        itinerary.max_price = formatted_decimal_plain(data.get('max_price'))

        if data.get('single_supplement') == 'True':
            itinerary.single_supplement = True
            #itinerary.single_supplement_price = formatted_decimal_plain(data.get('single_supplement_price'))
        else:
            itinerary.single_supplement = False
        itinerary.not_included = data.get('not_included')

        # day by day
        
        all_days = ItineraryDayDescription.objects.filter(itinerary=itinerary)
        for day in all_days:
            day.date_deleted = datetime.today()
            day.save()
        
        itinerary.days = data.get('days')
        for i in range(1, 1 + int(data.get('days'))):
            idd = ItineraryDayDescription.objects.filter(itinerary=itinerary, day_number=i)
            if idd.exists():
                idd = idd.first()
            else:
                idd = ItineraryDayDescription()
            idd.itinerary = itinerary
            idd.day_number = i
            idd.date_deleted = None
            idd.title = bleach.clean(data.get('day_{}_title'.format(i), ''))
            idd.description = bleach.clean(data.get('day_{}_description'.format(i), ''))
            idd.lodging = bleach.clean(data.get('day_{}_lodges'.format(i), ''))
            idd.save()
            parks = []
            parks_ids = data.getlist('day_{}_parks'.format(i))
            if parks_ids:
                for park_id in parks_ids:
                    parks.append(Park.objects.get(pk=park_id))
                idd.parks.set(parks)
            idd.save()

        if True:
            itinerary.save()
            # image
            if self.request.FILES.get('image'):
                itinerary.image = self.request.FILES.get('image')
            # save it!
            itinerary.activity_level = itinerary.calc_max_activity_level()
            itinerary.activity_level_name = itinerary.calc_activity_level_string()
            itinerary.save()
            messages.success(self.request, 'Tour package saved succesfully')
            if data.get('upload_photos') == '1':
                # take me to add_photos_itinerary itinerary.pk
                response = redirect('photos:add_tp_photos', itinerary_slug=itinerary.slug)
                return response
            else:
                # take me to tp dashboard
                response = redirect('backend:tour_operator_packages')
                return response
        else:
            messages.error(self.request, form.errors)
            return self.render_to_response(self.get_context_data(form=form))

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if 'pk' in kwargs:
            itinerary = Itinerary.objects.filter(pk=self.kwargs.get('pk'))
            itinerary = itinerary.filter(tour_operator=self.request.user.profile.tour_operator)
            if not itinerary.exists():
                messages.error(self.request, 'Not a valid tour package')
                response = redirect('backend:tour_operator_packages')
                return response
        return self.render_to_response(self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'slug' in kwargs:
            itinerary = Itinerary.objects.filter(slug=self.kwargs.get('slug'))
            itinerary = itinerary.filter(tour_operator=self.request.user.profile.tour_operator)
            itinerary = itinerary.first()
            itinerary_form = TourPackageForm(instance=itinerary)
            itinerary_form.fields['image'].label = 'Change itinerary photo *'
            itinerary_form.fields['image'].required = False
            context['itinerary'] = itinerary
            dd = ItineraryDayDescription.objects.filter(itinerary=itinerary)
            dd = dd.order_by('day_number')
            if dd.exists():
                context['dd'] = dd
                day_last = dd.last().day_number
                context['days_range'] = range(day_last + 1, 19)
            else:
                context['days_range'] = range(1, 19)
        else:
            itinerary_form = TourPackageForm(tour_operator=self.request.user.profile.tour_operator)
            context['days_range'] = range(1, 19)

        itinerary_form.fields['country_indexes'].queryset = self.request.user.profile.tour_operator.country_indexes
        context['display_name'] = 'Add tour package'
        context['tour_operator'] = self.request.user.profile.tour_operator
        itinerary_form.fields['parks'].queryset = Park.objects.all()
        context['form'] = itinerary_form
        countries = CountryIndex.objects.all().order_by('name')
        context['countries'] = countries
        parks = Park.objects.all().order_by('name')
        context['parks'] = parks

        countries_json = []
        for country in countries:
            country_json = {}
            country_json['id'] = country.id
            country_json['name'] = country.name
            country_json['parks'] = list(country.parks.all().order_by('name').values_list('id', flat=True))
            countries_json.append(country_json)
        game_drive, _ = Activity.objects.get_or_create(name='Game drives')
        context['vue_variables'] = {}
        context['vue_variables']['game_drive_id'] = game_drive.pk
        context['vue_variables']['countries_json'] = countries_json

        parks_json = []
        for park in parks:
            park_json = {}
            park_json['id'] = park.id
            park_json['name'] = park.name_short
            parks_json.append(park_json)
        context['vue_variables']['parks_json'] = parks_json
        return context


from rest_framework.views import APIView


# This view seems to have errors:
class SaveQuoteUpdate(APIView):

    def get(self, request, pk):
        quote = QuoteRequest.objects.filter(id=pk)
        tour_operator = self.request.user.profile.tour_operator
        quote = quote.filter(Q(tour_operator=tour_operator) | Q(itinerary__tour_operator=tour_operator))
        quote = quote.first()
        quote.seen = True
        quote.seen_on = datetime.today()
        quote.save()
        return JsonResponse({'status': pk})
