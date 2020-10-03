from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from operators.models import ItineraryFocusType, ItineraryDayDescription
from blog.models import Article
from places.models import Animal, CountryIndex
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from operators.models import TourOperator, ItineraryType, Itinerary, YASScore
from django.views.generic.edit import FormView
from django.contrib import messages
from operators.forms import QuoteRequestForm
from django.shortcuts import get_object_or_404, redirect
from core.utils import get_client_ip
from django.template.response import SimpleTemplateResponse
import yas.settings as settings
from post_office.models import EmailTemplate
from django.template import Template, Context
from post_office import mail
from django.urls import reverse
from core.models import EmailLog
from django.db.models import Count, Avg
from django.db.models import Subquery, OuterRef, IntegerField
from reviews.models import TourOperatorReview, ParkReview
from photos.models import Photo
from analytics.utils import log_action, get_request_country
from users.models import UserProfile
import json
from django.views.generic.base import View
from analytics.models import Action
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from operators.serializers import ItinerarySerializer
from django.views.decorators.clickjacking import xframe_options_exempt

# For API
from django.db.models import Q, F
from places.models import CountryIndex, Park, Activity, Language, Country
from places.serializers import CountryIndexSimpleSerializer, ParkSimpleSerializer
from places.serializers import ActivitySimpleSerializer, LanguageSerializer
from places.serializers import CountrySerializer
from operators.serializers import TourOperatorSerializer, ItinerarySerializer
from operators.serializers import ItineraryTypeSerializer
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from django.views.generic.base import ContextMixin


class RequestInfoThankYouView(TemplateView):
    template_name = "operators/quote_request_thanks.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class RequestInfoView(TemplateView):
    template_name = "operators/quote_request.html"

    def send_tour_operator_email(self, quote_request):
        from post_office import mail
        email_to = quote_request.tour_operator.email
        if settings.DEBUG:
            email_to = settings.TESTING_EMAILS
        link = reverse('backend:tour_operator_quotes')
        link = settings.BASE_URL +  link
        countries = ', '.join(quote_request.country_indexes.all().values_list('name_short',flat=True))
        context = {}
        context['member'] = quote_request.name
        context['tour_operator'] = quote_request.tour_operator.name
        context['countries'] = countries
        context['link'] = link
        mail.send(
            email_to,
            'Your African Safari <support@yourafricansafari.com>',
            template='quote_request',
            context=context,
        )

    def send_member_email(self, quote_request, details):
        from post_office import mail
        email_to = quote_request.email
        if settings.DEBUG:
            email_to = settings.TESTING_EMAILS
        context = {}
        context['member'] = quote_request.name
        context['tour_operator'] = quote_request.tour_operator.name
        context['sent_on'] = quote_request.date_created.strftime('%d %B')
        context['countries'] = ', '.join(quote_request.country_indexes.all().values_list('name_short',flat=True))
        context['date_of_trip'] = quote_request.date_trip.strftime('%d %B')
        context['days'] = quote_request.days
        context['size'] = quote_request.party_size
        context['comments'] = quote_request.additional_information
        context['details'] = details

        mail.send(
            email_to,
            'Your African Safari <support@yourafricansafari.com>',
            template='quote_request_member',
            context=context,
        )
    
    def send_member_follow_up_email(self, quote_request):
        from post_office import mail
        email_to = quote_request.email
        if settings.DEBUG:
            email_to = settings.TESTING_EMAILS
        link = settings.BASE_URL
        from datetime import datetime, timedelta
        when = datetime.now() + timedelta(days=2)
        context = {}
        context['member'] = quote_request.name
        context['tour_operator'] = quote_request.tour_operator.name
        context['date'] = quote_request.date_trip.strftime('%d %B')
        context['link'] = link
        mail.send(
            email_to,
            'Your African Safari <support@yourafricansafari.com>',
            template='quote_request_member_follow_up',
            context=context,
            scheduled_time=when
        )

    def save(self, request, *args, **kwargs):
        form = QuoteRequestForm(self.request.POST)
        operators = []
        country_indexes = CountryIndex.objects.filter(pk__in=self.request.POST.getlist('country_indexes'))
        details = []
        if form.is_valid():
            instance = form.save(commit=False)
            country = get_request_country(self.request)
            if country:
                instance.country = country
            it = self.request.POST.getlist('itineraries')
            if it:
                itineraries = Itinerary.objects.filter(id__in=it)
                for itinerary in itineraries:
                    instance.pk = None
                    instance.itinerary = itinerary
                    instance.tour_operator = itinerary.tour_operator
                    if self.request.user.is_authenticated:
                        instance.user = self.request.user
                    instance.save()
                    instance.country_indexes.set(country_indexes)
                    operators.append(itinerary.tour_operator.pk)
                    #add details for member email
                    link = reverse('tour_package', kwargs={'slug': itinerary.slug, 'pk': itinerary.pk})
                    link = settings.BASE_URL + link
                    details.append('<a href="{}" target="_blank">{}</a>'.format(link,itinerary.title))
                    self.send_tour_operator_email(instance)
            to = self.request.POST.getlist('tour_operators')
            if to:
                tour_operators = TourOperator.objects.filter(id__in=to)
                for tour_operator in tour_operators:
                    instance.pk = None
                    instance.tour_operator = tour_operator
                    if self.request.user.is_authenticated:
                        instance.user = self.request.user
                    instance.save()
                    instance.country_indexes.set(country_indexes)
                    operators.append(tour_operator.pk)
                    #add details for member email
                    link = reverse('tour_operator', kwargs={'slug': tour_operator.slug})
                    link = settings.BASE_URL + link
                    details.append('<a href="{}" target="_blank">{}</a>'.format(link,tour_operator.name))

                    self.send_tour_operator_email(instance)
        else:
            messages.error(self.request, form.errors)
            return self.render_to_response(self.get_context_data())
        #thank you email
        details = '<br>'.join(details)
        self.send_member_email(instance,details)
        #follow up email
        operators = set(operators)
        operators = TourOperator.objects.filter(pk__in=operators)
        for operator in operators:
            self.send_member_follow_up_email(instance)
        return redirect('tour_package_thanks')

    def post(self, request, *args, **kwargs):
        if 'save' in self.request.POST:
            return self.save(request, *args, **kwargs)
        from itertools import chain
        context = self.get_context_data()
        it = self.request.POST.getlist('itineraries')
        countries_ids = []
        if it:
            itineraries = Itinerary.objects.filter(id__in=it)
            context['itineraries'] = itineraries
            context['what'] = 'itinerary'
            for itinerary in itineraries.all():
                countries_ids += itinerary.country_indexes.all().values_list('id', flat=True)
        to = self.request.POST.getlist('tour_operators')
        if to:
            tour_operators = TourOperator.objects.filter(id__in=to)
            context['tour_operators'] = tour_operators
            context['what'] = 'tour operator'
            for tour_operator in tour_operators.all():
                countries_ids += tour_operator.country_indexes.all().values_list('id', flat=True)
        context['form'].fields['country_indexes'].queryset = CountryIndex.objects.filter(id__in=countries_ids)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = QuoteRequestForm()
        context['form'] = form
        if 'itinerary_pk' in kwargs:
            itinerary = Itinerary.objects.filter(pk=self.kwargs.get('itinerary_pk'))
            context['itineraries'] = itinerary
            context['form'].fields['country_indexes'].queryset = itinerary.first().country_indexes.all()
        if 'operator_pk' in kwargs:
            tour_operators = TourOperator.objects.filter(pk=self.kwargs.get('operator_pk'))
            context['tour_operators'] = tour_operators
            context['form'].fields['country_indexes'].queryset = tour_operators.first().country_indexes.all()
        # user is logged in
        if self.request.user.is_authenticated:
            form.fields['name'].initial = self.request.user.profile.display_name()
            form.fields['email'].initial = self.request.user.email
        return context

    # unused
    def get_form_kwargs(self):
        kwargs = super(RequestInfoView, self).get_form_kwargs()
        kwargs['tour_operator'] = get_object_or_404(TourOperator, slug=self.kwargs.get('slug'))
        if self.request.user.is_authenticated:
            kwargs['name'] = self.request.user.first_name + " " + self.request.user.last_name
            kwargs['email'] = self.request.user.email
        if self.request.GET.get('countries', ''):
            kwargs['countries'] = [get_object_or_404(CountryIndex, pk=x) for x in
                                   self.request.GET.get('countries').split(",")]

        if self.request.GET.get('regarding_text', ''):
            kwargs['regarding_text'] = self.request.GET.get('regarding_text', '')
        if self.request.GET.get("type", ""):
            kwargs["itinerary_type"] = get_object_or_404(ItineraryType, name=self.request.GET.get("type", ""))
        log_action(self.request, hit_object=self.kwargs.get('tour_operator'))
        return kwargs

    # unused
    def form_valid(self, form):
        countries = form.cleaned_data['country_indexes']
        quote_request = form.save(commit=False)
        tour_operator = get_object_or_404(TourOperator, slug=self.kwargs.get('slug'))
        quote_request.tour_operator = tour_operator
        quote_request.ip_address = get_client_ip(self.request)
        quote_request.user = self.request.user
        quote_request.save()
        quote_request.country_indexes.set(countries)
        quote_request.save()

        self.send_more_information_email(quote_request)
        self.send_user_information_summary_email([quote_request])

        context = {'base_url': settings.BASE_URL, 'back_to': self.request.GET.get('back_to', '')}

        t = SimpleTemplateResponse('operators/quote_request_thanks.html', context)
        return t

    # unused
    def send_more_information_email(self, quote_request):
        subject = "Quote request from: %s [Ref %d]" % (quote_request.name, quote_request.pk)
        template = EmailTemplate.objects.get(name="more_information")
        t = Template(template.html_content)
        c = Context({'quoterequest': quote_request, 'base_url': settings.BASE_URL})
        mail_body = t.render(c)

        email_string = ",".join(quote_request.tour_operator.email_recipient_list())

        log_entry = EmailLog()
        log_entry.address_to = email_string
        log_entry.address_from = 'Your African Safari <support@yourafricansafari.com>'
        log_entry.subject = subject
        log_entry.body = mail_body
        log_entry.save()
        c = Context({'quoterequest': quote_request, 'base_url': settings.BASE_URL, 'emaillog_id': log_entry.pk})
        mail.send(
            email_string,
            'Your African Safari <support@yourafricansafari.com>',
            subject=subject,
            html_message=t.render(c),
        )

    # unused
    def send_user_information_summary_email(self, quote_requests):

        if len(quote_requests) > 1:
            shortlist_link = self.request.build_absolute_uri(
                reverse('manage_shortlist', args=(",".join([str(x.pk) for x in quote_requests]),)))
        else:
            shortlist_link = self.request.build_absolute_uri(
                reverse('tour_operator', args=(quote_requests[0].tour_operator.slug,)))

        subject = "Summary of quote request [ref: %s]" % ",".join([str(x.pk) for x in quote_requests])
        template = EmailTemplate.objects.get(name="user_information_summary")
        t = Template(template.html_content)
        c = Context({'quote_requests': quote_requests, 'shortlist_link': shortlist_link, 'base_url': settings.BASE_URL})
        mail_body = t.render(c)

        email_string = quote_requests[0].name + " <" + quote_requests[0].email + ">"
        log_entry = EmailLog()
        log_entry.address_to = email_string
        log_entry.address_from = 'Your African Safari <support@yourafricansafari.com>'
        log_entry.subject = subject
        log_entry.body = mail_body
        log_entry.save()
        c = Context({'quote_requests': quote_requests, 'shortlist_link': shortlist_link, 'base_url': settings.BASE_URL,
                     'emaillog_id': log_entry.pk})
        mail.send(
            email_string,
            'Your African Safari <support@yourafricansafari.com>',
            subject=subject,
            html_message=t.render(c),
        )

        c = Context({'quote_requests': quote_requests, 'shortlist_link': shortlist_link, 'base_url': settings.BASE_URL})
        mail.send(
            'Your African Safari <support@yourafricansafari.com>',
            'Your African Safari <support@yourafricansafari.com>',
            subject=subject,
            html_message=t.render(c),
        )


@method_decorator(csrf_exempt, name='dispatch')
class TourOperatorReviewKuduView(View):

    def post(self, request, **kwargs):

        try:
            obj = TourOperatorReview.objects.filter(pk=self.kwargs.get("pk")).first()
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
            if Action.objects.filter(action_type="K", user=request.user, tour_operator_review=obj).count():
                return JsonResponse(
                    {'message': 'Thanks, but you already gave a kudu', 'kudus': kudu_count, 'text': text})
            else:
                action = Action()
                action.content_type = ContentType.objects.get(model='touroperatorreview')
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

class BaseContextMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super(BaseContextMixin, self).get_context_data(**kwargs)
        if self.kwargs.get('slug'):
            tour = TourOperator.objects.get(slug=self.kwargs.get('slug'))
        else:
            from django.http import Http404
            raise Http404("No tour operator")
        context['tour_operator'] = tour

        return context


@method_decorator(xframe_options_exempt, name='dispatch')           
class TourOperatorWidgetOneDetailView(TemplateView, BaseContextMixin):
    model = TourOperator
    template_name = "operators/tour_operator_widget_1.html"
    
    def get_context_data(self, **kwargs):
        context = super(TourOperatorWidgetOneDetailView, self).get_context_data(**kwargs)
        return context

@method_decorator(xframe_options_exempt, name='dispatch')           
class TourOperatorWidgetTwoDetailView(TemplateView, BaseContextMixin):
    model = TourOperator
    template_name = "operators/tour_operator_widget_2.html"
    
    def get_context_data(self, **kwargs):
        context = super(TourOperatorWidgetTwoDetailView, self).get_context_data(**kwargs)
        return context

@method_decorator(xframe_options_exempt, name='dispatch')           
class TourOperatorWidgetFourDetailView(TemplateView, BaseContextMixin):
    model = TourOperator
    template_name = "operators/tour_operator_widget_4.html"
    
    def get_context_data(self, **kwargs):
        context = super(TourOperatorWidgetFourDetailView, self).get_context_data(**kwargs)
        context['reviews'] = TourOperatorReview.objects.filter(tour_operator=context['tour_operator'])[:3]
        return context



class TourOperatorDetailView(TemplateView):
    model = TourOperator
    template_name = "operators/tour_operator.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('slug'):
            tour = TourOperator.objects.get(slug=self.kwargs.get('slug'))
        else:
            from django.http import Http404
            raise Http404("No tour operator")
        tour.annotated = TourOperator.objects.filter(id=tour.id).annotate(
            review_avg=Avg('tour_operator_reviews__overall_rating')).annotate(
            review_count=Count('tour_operator_reviews', distinct=True)).annotate(
            photo_count=Count('photos', distinct=True)).annotate(
            package_count=Count('itineraries', distinct=True)).annotate(
            vehicle_avg=Avg('tour_operator_reviews__vehicle_rating')).annotate(
            meet_and_greet_avg=Avg('tour_operator_reviews__meet_and_greet_rating')).annotate(
            responsiveness_avg=Avg('tour_operator_reviews__responsiveness_rating')).annotate(
            safari_quality_avg=Avg('tour_operator_reviews__safari_quality_rating')).annotate(
            itinerary_quality_avg=Avg('tour_operator_reviews__itinerary_quality_rating')).first()

        # focused review
        if 'review' in kwargs:
            o_review = TourOperatorReview.objects.get(pk=self.kwargs.get('review'))
            temp = get_template('operators/tour_operator_includes/tour_reviews_cards.html')
            result = temp.render({'tour_reviews': [o_review], 'tour': tour, 'focused': True})
            context['review_focus'] = result

        # first of three
        context['tour_vehicle_reviews_average'] = tour.annotated.vehicle_avg
        context['tour_meet_and_greet_reviews_average'] = tour.annotated.meet_and_greet_avg
        context['tour_responsiveness_reviews_average'] = tour.annotated.responsiveness_avg
        context['tour_safari_quality_reviews_average'] = tour.annotated.safari_quality_avg
        context['tour_itinerary_quality_reviews_average'] = tour.annotated.itinerary_quality_avg
        # sencond of three
        context['tour_countries'] = CountryIndex.objects.filter(itineraries__tour_operator=tour).distinct()
        # context['tour_countries'] = CountryIndex.objects.filter(parks__in=tour.parks.all())

        context['tour_reviews_average'] = tour.annotated.review_avg
        context['tour_reviews_count'] = tour.annotated.review_count
        context['tour_packages_count'] = tour.annotated.package_count

        context['tour_reviews'] = TourOperatorReview.objects.filter(tour_operator=tour, status="AC").order_by(
            '-date_modified')[:10]
        context['tour_reviews_total'] = tour.tour_operator_reviews.all().count()

        tour_user_profile = UserProfile.objects.filter(tour_operator=tour).first()

        context['tour_quick_respond'] = tour.quick_to_respond()
        if tour_user_profile:
            context['tour_park_reviews'] = ParkReview.objects.filter(user=tour_user_profile.user)
            context['tour_articles'] = Article.objects.filter(user=tour_user_profile.user)[:5]
            context['tour_articles_total'] = Article.objects.filter(user=tour_user_profile.user)[:5].count()
        context['tour_photos'] = Photo.objects.filter(draft=False, tour_operator=tour, image__isnull=False).exclude(
            image__exact='').order_by(
            '-date_modified')[:20]
        context['tour_photos_count'] = Photo.objects.filter(draft=False, tour_operator=tour,
                                                            image__isnull=False).exclude(
            image__exact='').order_by(
            '-date_modified')[:20].count()
        if context['tour_photos']:
            context['tour_photos_first_id'] = context['tour_photos'].first().id

        tour.is_fav_ = tour.is_fav(self.request)
        context['tour'] = tour

        log_action(self.request, hit_object=tour)

        return context

    def post(self, request, *args, **kwargs):
        tour = TourOperator.objects.get(slug__exact=self.kwargs.get('slug'))

        review_id_focus = json.loads(request.body)['focus_review']
        if not review_id_focus:
            review_id_focus = 0

        is_sorting = json.loads(request.body)['is_sorting']
        order = int(json.loads(request.body)['sort'])
        limit = int(json.loads(request.body)['limit'])

        order_by = '-date_created'

        if order == 1:
            order_by = '-date_modified'
        elif order == 2:
            order_by = 'date_modified'

        limit1 = 0 if is_sorting else limit - 10
        limit2 = limit
        total_reviews = TourOperatorReview.objects.filter(
            tour_operator__pk=tour.pk).count()

        reviews = TourOperatorReview.objects.filter(
            tour_operator__pk=tour.pk, status="AC").order_by(order_by)[limit1:limit2]
        temp = get_template('operators/tour_operator_includes/tour_reviews_cards.html')
        result = temp.render({'tour_reviews': reviews})

        reviews_capped = False
        if total_reviews <= limit2:
            reviews_capped = True

        dictionary = {'capped': reviews_capped, 'reviews': result}

        return HttpResponse(json.dumps(dictionary), content_type="application/json")


class TourOperatorView(TemplateView):
    model = TourOperator
    template_name = "operators/all_tour_operators.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        log_action(self.request)

        context['filter_variants_country_and_park'] = json.dumps(countries_and_parks())

        luxury_level_choices = dict(TourOperator.LUXURY_LEVEL_CHOICES)
        luxury_focus = [
            {
                'id': TourOperator.LUXURY_LEVEL_BUDGET,
                'title': luxury_level_choices[TourOperator.LUXURY_LEVEL_BUDGET],
                'count': TourOperator.objects.filter(luxury_level = TourOperator.LUXURY_LEVEL_BUDGET).count()
            },
            {
                'id': TourOperator.LUXURY_LEVEL_MID_LEVEL,
                'title': luxury_level_choices[TourOperator.LUXURY_LEVEL_MID_LEVEL],
                'count': TourOperator.objects.filter(luxury_level = TourOperator.LUXURY_LEVEL_MID_LEVEL).count()
            },
            {
                'id': TourOperator.LUXURY_LEVEL_ULTRA_SAFARI,
                'title': luxury_level_choices[TourOperator.LUXURY_LEVEL_ULTRA_SAFARI],
                'count': TourOperator.objects.filter(luxury_level = TourOperator.LUXURY_LEVEL_ULTRA_SAFARI).count()
            },
        ]
        context['luxury_focus'] = json.dumps(luxury_focus)

        ratings = []
        for i in range(0, 5):
            ratings.append({ 'id': i + 1, 'rating': i + 1, 'count': TourOperator.objects.filter(average_rating = i + 1).count() })
        context['minimum_rating'] = json.dumps(ratings)

        languages = Language.objects.all()
        languages_serializer = LanguageSerializer(languages, many=True)
        context['languages'] = json.dumps(languages_serializer.data)

        headquarters = Country.objects.all()
        headquarters_serializer = CountrySerializer(headquarters, many=True)
        context['headquarters'] = json.dumps(headquarters_serializer.data)

        tour_operator_that = []
        operator_that_choices = TourOperator.operator_that_choices()
        for key in operator_that_choices:
            rule = operator_that_choices[key]
            q = TourOperator.objects
            if rule['annotate']: q = q.annotate(subquery_alias = rule['annotate'])
            q = q.filter(rule['query'])
            count = q.count()
            tour_operator_that.append({
                'id': key,
                'title': rule['title'],
                'count': count
            })
        context['tour_operator_that'] = json.dumps(tour_operator_that)

        slug = self.slug(context)
        context['slug'] = json.dumps(slug)

        context['head'] = self.page_head(context, slug)

        return context

    def slug(self, context):
        slug = context.get('country', '')
        if not slug: return None
        country_slug = CountryIndex.objects.filter(slug = slug).first()
        if country_slug: return {
            'model': 'CountryIndex',
            'id': country_slug.id,
            'value': country_slug.name_short,
            'slug': country_slug.slug,
        }
        else:
            park_slug = Park.objects.filter(slug = slug).first()
            if park_slug: return {
                'model': 'Park',
                'id': park_slug.id,
                'value': park_slug.name_short,
                'slug': park_slug.slug,
            }

        return None

    def title_short_names(self, entities_list):
        names = []
        for entity in entities_list:
            fields = entity['model'].objects.filter(id__in = entity['ids']).values('name_short')
            names.extend(list(d['name_short'] for d in fields))
        return ', '.join(list(set(names)))

    def page_head(self, context, slug):

        self.slug = slug

        queryset = TourOperatorRollupAPIView.get_queryset(self)
        positions_count = queryset.count()

        places = self.title_short_names([
            { 'model': CountryIndex, 'ids': queryset.countries },
            { 'model': Park, 'ids': queryset.parks }
        ])

        if not places: places = 'Africa'

        header_name = 'African'

        if len(queryset.countries):
            country = CountryIndex.objects.filter(id__in = queryset.countries).first()
            if country: header_name = country.name_short
        elif len(queryset.parks):
            park = Park.objects.filter(id__in = queryset.parks).first()
            if park: header_name = park.name_short

        return {
            'title': 'Safari Tour Operators for {places}'\
                .format(count = positions_count, places = places),
            'description': 'Choose from {count} safari tour operators in {places}'\
                .format(count = positions_count, places = places),
            'header': header_name + ' safari tour operators'
        }


class TourPackageView(TemplateView):
    model = Itinerary
    template_name = "operators/tour_package.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        itinerary = Itinerary.objects.get(pk=self.kwargs.get('pk'))
        itinerary.is_fav_ = itinerary.is_fav(self.request)

        context['itinerary'] = itinerary
        itinerary_days = ItineraryDayDescription.objects.filter(itinerary=itinerary).filter(date_deleted__isnull=True).order_by('day_number')
        context['itinerary_days'] = itinerary_days
        country_index = CountryIndex.objects.get(id=1)

        parks = itinerary.parks.all()
        lat = 0
        lon = 0
        for park in parks:
            lat += park.latitude
            lon += park.longitude

        lat = str(lat/len(parks))
        lon = str(lon/len(parks))

        context['parks_data'] = serializers.serialize('json', itinerary.parks.all(),
                                                      fields=('name', 'name_short', 'latitude', 'longitude', 'slug'))


        if itinerary.activity_level_name == 'Easy':
            battery_level = 'empty'
        elif itinerary.activity_level_name == 'Moderate':
            battery_level = 'half'
        else:
            battery_level = 'full'

        context['battery_level'] = battery_level

        context['country_data'] = [{"fields": {"name": "center", "slug": "center", "latitude": lat, "longitude": lon}}]

        tour = itinerary.tour_operator

        tour.annotated = TourOperator.objects.filter(id=tour.id).annotate(
            review_avg=Avg('tour_operator_reviews__overall_rating')).annotate(
            review_count=Count('tour_operator_reviews', distinct=True)).annotate(
            photo_count=Count('photos', distinct=True)).annotate(
            package_count=Count('itineraries', distinct=True)).annotate(
            vehicle_avg=Avg('tour_operator_reviews__vehicle_rating')).annotate(
            meet_and_greet_avg=Avg('tour_operator_reviews__meet_and_greet_rating')).annotate(
            responsiveness_avg=Avg('tour_operator_reviews__responsiveness_rating')).annotate(
            safari_quality_avg=Avg('tour_operator_reviews__safari_quality_rating')).annotate(
            itinerary_quality_avg=Avg('tour_operator_reviews__itinerary_quality_rating')).first()


        context['tour_vehicle_reviews_average'] = tour.annotated.vehicle_avg
        context['tour_meet_and_greet_reviews_average'] = tour.annotated.meet_and_greet_avg
        context['tour_responsiveness_reviews_average'] = tour.annotated.responsiveness_avg
        context['tour_safari_quality_reviews_average'] = tour.annotated.safari_quality_avg
        context['tour_itinerary_quality_reviews_average'] = tour.annotated.itinerary_quality_avg
        context['tour_reviews_average'] = tour.annotated.review_avg

        context['operator'] = tour
        serializer = ItinerarySerializer()

        all_tours = Itinerary.objects.filter(date_deleted__isnull=True).filter(tour_operator=tour).exclude(id=itinerary.id).order_by('-date_modified')
        for tour in all_tours:
            tour.serialized = serializer._main_features(tour)

        context['all_tours_count'] = all_tours.count()
        related_tours = all_tours[:6]
        for related_tour in related_tours:
            related_tour.is_fav_ = related_tour.is_fav(self.request)
        context['related_tours'] = related_tours
    
        log_action(self.request, hit_object=itinerary)
        return context


class ItineraryView(TemplateView):
    model = Itinerary
    template_name = "operators/all_tour_packages.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        log_action(self.request)

        context['filter_variants_country_and_park'] = json.dumps(countries_and_parks())

        price_range = Itinerary.objects.aggregate(Max('search_price'), Min('search_price'))
        context['min_price'] = price_range['search_price__min']
        context['max_price'] = price_range['search_price__max']

        focus_type_main = ItineraryFocusType.objects.get(name='Primary').pk
        focus_type_second = ItineraryFocusType.objects.get(name='Secondary').pk
        main_focus_activities = Activity.objects.filter(focus_type__in=[focus_type_main]).order_by('name_short')
        main_focus_serializer = ActivitySimpleSerializer(main_focus_activities, many=True)
        context['main_focus_activities'] = json.dumps(main_focus_serializer.data)
        second_focus_activities = Activity.objects.filter(focus_type__in=[focus_type_second]).order_by('name_short')
        second_focus_serializer = ActivitySimpleSerializer(second_focus_activities, many=True)
        context['second_focus_activities'] = json.dumps(second_focus_serializer.data)

        itinerary_types = ItineraryType.objects.all()
        itinerary_types_serializer = ItineraryTypeSerializer(itinerary_types, many=True)
        context['itinerary_types'] = json.dumps(itinerary_types_serializer.data)

        slug = self.slug(context)
        context['slug'] = json.dumps(slug)

        context['head'] = self.page_head(context, slug)

        return context

    def slug(self, context):
        slug = context.get('country', '')
        if not slug: return None
        country_slug = CountryIndex.objects.filter(slug = slug).first()
        if country_slug: return {
            'model': 'CountryIndex',
            'id': country_slug.id,
            'value': country_slug.name_short,
            'slug': country_slug.slug,
        }
        else:
            park_slug = Park.objects.filter(slug = slug).first()
            if park_slug: return {
                'model': 'Park',
                'id': park_slug.id,
                'value': park_slug.name_short,
                'slug': park_slug.slug,
            }
            else:
                operator_slug = TourOperator.objects.filter(slug = slug).first()
                if operator_slug: return {
                    'model': 'TourOperator',
                    'id': operator_slug.id,
                    'value': operator_slug.name,
                    'slug': operator_slug.slug,
                }
        return None

    def title_short_names(self, entities_list):
        names = []
        for entity in entities_list:
            fields = entity['model'].objects.filter(id__in = entity['ids']).values('name_short')
            names.extend(list(d['name_short'] for d in fields))
        return ', '.join(list(set(names)))

    def page_head(self, context, slug):

        self.slug = slug

        queryset = TourPackageRollupAPIView.get_queryset(self)
        positions_count = queryset.count()

        places = self.title_short_names([
            { 'model': CountryIndex, 'ids': queryset.countries },
            { 'model': Park, 'ids': queryset.parks }
        ])

        focus = self.title_short_names([
            { 'model': Activity, 'ids': [queryset.main_focus] },
            { 'model': Activity, 'ids': queryset.secondary_focus }
        ])

        if not places: places = 'African'
        if focus: focus = ' with ' + focus

        header_name = 'African'

        if len(queryset.countries):
            country = CountryIndex.objects.filter(id__in = queryset.countries).first()
            if country: header_name = country.name_short
        elif len(queryset.parks):
            park = Park.objects.filter(id__in = queryset.parks).first()
            if park: header_name = park.name_short
        if queryset.main_focus:
            main_focus = Activity.objects.filter(id = queryset.main_focus).first()
            if main_focus:
                # header_name = header_name + ' ' + main_focus.name_short
                places = places + ' ' + main_focus.name_short

        if slug and slug['model'] == 'TourOperator':
            places = slug['value'] + ' ' + places

        return {
            'title': '{places} Safari Tours'\
                .format(count = positions_count, places = places),
            'description': 'Choose from {count} safari tour packages in {places}{focus}'\
                .format(count = positions_count, places = places, focus = focus),
            'header': header_name + ' safari tour packages'
        }



class TourOperatorReviewView(TemplateView):
    model = TourOperator
    template_name = "operators/tour_operator_reviews.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        log_action(self.request)
        return context


class ManageShortlistView(TemplateView):
    template_name = "operators/manage_shortlist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        log_action(self.request)
        return context


from rest_framework.views import APIView

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100


from datetime import datetime, timedelta
from django.db.models import Max, Min


class TourOperatorRollupAPIView(generics.ListAPIView):
    serializer_class = TourOperatorSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        params = self.request.GET
        queryset = TourOperator.objects.all()
        parks = params.getlist('parks[]', []) + params.getlist('parks', [])
        countries = params.getlist('countries[]', []) + params.getlist('countries', [])
        from_date = params.get('from_date', None)
        luxury_focus = params.get('luxury_focus', None)
        rating = params.get('rating', None)
        languages = params.getlist('languages[]', []) + params.getlist('languages', [])
        headquarters = params.getlist('headquarters[]', []) + params.getlist('headquarters', [])
        that = params.getlist('that[]', []) + params.getlist('that', [])
        ordering = params.get('ordering', '-yas_score')
        # slug. if load with api
        slug = json.loads(params.get('slug', 'null'))

        # slug. if load page and render from server
        if hasattr(self, 'slug') and self.slug:
            slug = self.slug

        if slug:
            if slug['model'] == 'CountryIndex': countries = [slug['id']] + countries
            if slug['model'] == 'Park': parks = [slug['id']] + parks

        if len(parks) or len(countries):
            queryset = queryset.filter(Q(country_indexes__in=countries) | Q(parks__in=parks))

        if luxury_focus:
            queryset = queryset.filter(luxury_level = luxury_focus)

        if rating:
            queryset = queryset.filter(average_rating__gte = rating)
        
        if len(languages):
            queryset = queryset.filter(languages__in=languages)
        
        if len(headquarters):
            queryset = queryset.filter(headquarters__in=headquarters)

        if len(that):
            that_choices = TourOperator.operator_that_choices()
            for t in that:
                if t in that_choices:
                    rule = that_choices[t]
                    if rule['annotate']: queryset = queryset.annotate(subquery_alias = rule['annotate'])
                    queryset = queryset.filter(rule['query'])

        queryset = queryset.distinct()
        queryset = queryset.annotate(new_yas_score=F('yas_score'))
        if ordering and ordering == '-yas_score':
            #yas score by country                
            if len(parks) or len(countries):
                parks_countries = Park.objects.filter(id__in=parks).values_list('country_indexes__id', flat=True)
                all_ids = countries + list(parks_countries)
                yas_score_subquery = YASScore.objects \
                    .filter(tour_operator_id=OuterRef('id')) \
                    .filter(country_index_id__in=all_ids) \
                    .order_by().values('tour_operator_id')
                packages_yas_score_avg = yas_score_subquery \
                    .annotate(avg=Avg('yas_score')) \
                    .values('avg')
                queryset = queryset.annotate(
                    new_yas_score=Subquery(packages_yas_score_avg, output_field=IntegerField())) \
                    .order_by('-new_yas_score')
        else:
            queryset = queryset.order_by(ordering)
        queryset.parks = parks
        queryset.countries = countries
        return queryset


class TourPackageRollupAPIView(generics.ListAPIView):
    # TODO: add ordering
    serializer_class = ItinerarySerializer
    pagination_class = StandardResultsSetPagination

    def months_between(self, start, end):
        months = []
        cursor = start
        while cursor <= end:
            if cursor.month not in months:
                months.append(cursor.month)
            cursor += timedelta(weeks=1)
        return months

    def get_queryset(self):
        params = self.request.GET
        queryset = Itinerary.objects.filter(date_deleted__isnull=True)
        parks = params.getlist('parks[]', []) + params.getlist('parks', [])
        countries = params.getlist('countries[]', []) + params.getlist('countries', [])
        days = params.get('days', None)
        min_price = params.get('min_price', None)
        max_price = params.get('max_price', None)
        from_date = params.get('from_date', None)
        to_date = params.get('to_date', None)
        travelers = params.get('adult_travelers', None)
        main_focus = params.get('main_focus', None)
        secondary_focus = params.getlist('secondary_focus[]', []) + params.getlist('secondary_focus', [])
        safary_preference = params.get('safary_preference', None)
        activity_levels = params.getlist('activity_levels[]', []) + params.getlist('activity_levels', [])
        ordering = params.get('ordering', '-id')
        operators = []
        # slug. if load with api
        slug = json.loads(params.get('slug', 'null'))

        # slug. if load page and render from server
        if hasattr(self, 'slug') and self.slug:
            slug = self.slug

        if slug:
            if slug['model'] == 'CountryIndex': countries = [slug['id']] + countries
            if slug['model'] == 'Park': parks = [slug['id']] + parks
            if slug['model'] == 'TourOperator': operators.append(slug['id'])

        if len(parks) or len(countries):
            queryset = queryset.filter(Q(country_indexes__in=countries) | Q(parks__in=parks))

        if (len(operators)):
            queryset = queryset.filter(tour_operator__in = operators)

        if days:
            queryset = queryset.filter(days=days)

        price_query = Q()
        if min_price: price_query &= Q(search_price__gte=min_price)
        if max_price: price_query &= Q(search_price__lte=max_price)
        if (min_price or max_price):
            queryset = queryset.filter(price_query)

        # Logic of filter: get all months between dates.
        # Check that package contain all this months.
        # Used "Spanning multi-valued relationships": https://docs.djangoproject.com/en/dev/topics/db/queries/
        months = []
        if from_date: from_date = datetime.strptime(from_date, '%m/%d/%Y')
        if to_date: to_date = datetime.strptime(to_date, '%m/%d/%Y')
        if from_date and to_date:
            months = self.months_between(from_date, to_date)
        elif from_date:
            months.append(from_date.month)
        elif to_date:
            months.append(to_date.month)
        if len(months):
            for month in months:
                queryset = queryset.filter(months=month)

        # TODO: Hmm..
        # if travelers:
        #     queryset.filter()

        if len(secondary_focus):
            queryset = queryset.filter(secondary_focus_activity__in=secondary_focus)

        if safary_preference:
            queryset = queryset.filter(itinerary_type_id=safary_preference)

        if main_focus:
            queryset = queryset.filter(safari_focus_activity_id=main_focus)

        if len(activity_levels):
            ACTIVITIES = {
                'Easy': 'Easy',
                'Moderate': 'Moderate',
                'Strenuous': 'Strenuous',
            }
            activity_levels_query = Q()

            if 'Easy' in activity_levels:
                activity_levels_query |= Q(
                    (
                        Q(activity_level_name=ACTIVITIES['Easy'])
                    ) | (
                        Q(activity_level_name='')
                    )
                )
            if 'Moderate' in activity_levels:
                activity_levels_query |= Q(activity_level_name=ACTIVITIES['Moderate'])
            if 'Strenuous' in activity_levels:
                activity_levels_query |= Q(activity_level_name=ACTIVITIES['Strenuous'])

            queryset = queryset.filter(activity_levels_query)
        
        queryset = queryset.annotate(yas_score=F('tour_operator__yas_score'))
        if ordering:    
            #yas score
            if ordering == '-yas_score':
                #yas score by country                
                if len(parks) or len(countries):
                    parks_countries = Park.objects.filter(id__in=parks).values_list('country_indexes__id', flat=True)
                    all_ids = countries + list(parks_countries)
                    yas_score_subquery = YASScore.objects \
                        .filter(tour_operator_id=OuterRef('tour_operator_id')) \
                        .filter(country_index_id__in=all_ids) \
                        .order_by().values('tour_operator_id')
                    packages_yas_score_avg = yas_score_subquery \
                        .annotate(avg=Avg('yas_score')) \
                        .values('avg')
                    queryset = queryset.annotate(
                        yas_score=Subquery(packages_yas_score_avg, output_field=IntegerField())) \
                        .order_by('-yas_score')
                else:
                    #when there's no country selected
                    #nothing to do
                    pass
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by(F('safari_focus_activity__priority').desc(nulls_last=True))
        queryset = queryset.distinct()
        
        # For page title and discription in ItineraryView.page_head
        queryset.parks = parks
        queryset.countries = countries
        queryset.main_focus = main_focus
        queryset.secondary_focus = secondary_focus

        return queryset

def countries_and_parks():
    countries = CountryIndex.objects.all()
    countries_serializer = CountryIndexSimpleSerializer(countries, many=True)

    parks = Park.objects.all()
    parks_serializer = ParkSimpleSerializer(parks, many=True)

    countries_and_parks = parks_serializer.data + countries_serializer.data

    def tuple_sort(m):
        for m1 in m:
            if m1 == 'is_top':
                d = dict(m)
                return d[m1]
        return False

    countries_and_parks.sort(key=tuple_sort, reverse=True)

    for i, item in enumerate(countries_and_parks):
        item['id'] = i
    return countries_and_parks
    
