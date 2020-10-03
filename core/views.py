from django.contrib.auth.decorators import login_required
from places.models import CountryIndex
from django.http import HttpResponse
from django.template import loader
from places.models import CountryIndex
from django.contrib import messages
from django.views.generic import TemplateView, FormView
from django.views.generic.detail import DetailView
from core.models import Page
from django.views.generic.base import TemplateView
import random
from django.shortcuts import redirect
from operators.models import TourOperator
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from analytics.models import Action
from core.utils import parse_variables
from places.models import CountryIndex, Park
from django.views.decorators.http import require_GET
from analytics.utils import log_action
from backend.forms import CompanyInfoForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

@require_GET
def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Disallow: /park/manage-photos",
        "Disallow: /tour-operator/manage-photos",
        "Disallow: /create/",
        "Disallow: /activate_complete/",
        "Disallow: /activate/",

    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


# This view seems to have errors:
class PhotoKudoView(APIView):

    def get(self, request, photo_pk):
        photo = get_object_or_404(Photo, pk=photo_pk)
        action = Action()
        action.action_type = Action.KUDU
        action.user = request.user
        action.content_object = photoaction.save()
        return Response(action)

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

class JoinUsThankYouView(MemberRequiredLoginView, TemplateView):
    template_name = "core/join_us_thank_you.html"
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class JoinUsView(MemberRequiredLoginView, TemplateView):
    template_name = "core/join_us.html"
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['disable_footer'] = False
        form = CompanyInfoForm(request.POST)
        form.fields['name'].widget.attrs['readonly'] = False
        form.fields['email'].widget.attrs['readonly'] = False
        form.fields['website'].widget.attrs['readonly'] = False
        context['form'] = form
        if form.is_valid():
            instance = form.save(commit=False)
            existent = TourOperator.objects.filter(website=instance.website)
            if existent:
                messages.error(self.request, 'This company is already listed on YAS. If you work for this company and would like access, please contact us to yas@yourafricansafari.com')
            else:
                import uuid
                form.cleaned_data['slug'] = uuid.uuid4()
                form.save()
                instance.draft = True
                from django.template.defaultfilters import slugify
                #todo improve slugify, rename pk if not required
                instance.slug = slugify("{}-{}".format(instance.pk, instance.name))
                self.request.user.profile.tour_operator = instance
                self.request.user.profile.save()
                instance.user = self.request.user
                instance.save()
                messages.success(self.request, 'Application sent')
                return redirect('join_thank_you')
        else:
            pass
            #messages.error(self.request, 'There was an error with your submission {}'.format(form.errors))
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if self.request.user.profile.is_tour_operator():
            messages.error(self.request, 'Your user is already registered as a company with YAS')
            #return redirect('home')
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CompanyInfoForm()
        context['form'].fields['name'].widget.attrs['readonly'] = False
        context['form'].fields['website'].widget.attrs['readonly'] = False
        context['form'].fields['email'].widget.attrs['readonly'] = False
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
        log_action(self.request)
        return context


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        featured_tour_operators = TourOperator.objects.all()
        featured_tour_operators = featured_tour_operators.exclude(slug=None)
        featured_tour_operators = featured_tour_operators.exclude(slug='')
        featured_tour_operators = featured_tour_operators.order_by('-date_created')[:4]        
        context['masthead_number'] = random.randint(1, 6)
        context['masthead_number_lg'] = random.randint(1, 3)  
        context['featured_tour_operators'] = featured_tour_operators
        context['alert_success_activation'] = not not self.request.GET.get('success_activation')
        context['alert_error_activation'] = not not self.request.GET.get('error_activation')
        log_action(self.request)
        return context


class PageView(TemplateView):
    template_name = "core/page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = Page.objects.get(slug=self.kwargs.get('page_name'))
        context['page'] = page
        context['content'] = parse_variables(page.parse_content())
        log_action(self.request,hit_object=page)
        return context


class CountriesListView(TemplateView):
    template_name = "core/countries.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        countries = CountryIndex.objects.all()
        context['countries'] = countries
        log_action(self.request)
        return context
