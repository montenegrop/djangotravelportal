from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from backend.inc_forms.admin import *
from operators.models import TourOperator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from django.shortcuts import redirect
from django.contrib.auth.models import User
from photos.models import Photo
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from backend.forms import ArticleForm, TourOperatorReviewForm, ParkReviewForm
from reviews.models import ParkReview,TourOperatorReview,AbstractReview

class AdminRequiredLoginView(UserPassesTestMixin, LoginRequiredMixin):

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['disable_footer'] = True
        return context



class AdminMembersView(AdminRequiredLoginView, TemplateView):
    template_name = "backend/admin/members.html"

    def get(self, request, *args, **kwargs):
        #DELETE
        if self.request.GET.get('delete'):
            pk = self.request.GET.get('delete')
            obj = User.objects.get(pk=pk)
            obj.profile.date_deleted = datetime.today()
            obj.is_active = False
            obj.save()
            #remove associated stuff with member TODO
            Photo.objects.filter(user=obj).delete()
            messages.success(self.request, 'Member deleted')
            return redirect('backend:admin_members')    
        #PAGINATION
        form = MemberFilterForm(self.request.GET or None)
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
            context['form'] = MemberFilterForm()
        objs = User.objects.filter(is_active=True)
        # filter logic
        if 'form' in kwargs and kwargs['form']:
            search_by = kwargs['form'].cleaned_data.get('search_by')
            if search_by:

                objs = objs.filter(Q(username__contains=search_by) | Q(email__contains=search_by) | Q(profile__screen_name__contains=search_by))
            order_by = kwargs['form'].cleaned_data.get('order_by')
            if order_by:
                objs = objs.order_by(order_by)
            
        # sort
        #sort = self.request.GET.get('sort', '')
        #how = self.request.GET.get('how', '')
        #if sort:
        #    tour_operators = tour_operators.order_by(how + sort)

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


class AdminTourOperatorView(AdminRequiredLoginView, TemplateView):
    template_name = "backend/admin/tour_operators.html"

    def get(self, request, *args, **kwargs):
        #DELETE
        if self.request.GET.get('delete_tour_operator'):
            pk = self.request.GET.get('delete_tour_operator')
            operator = TourOperator.objects.get(pk=pk)
            operator.date_deleted = datetime.today()
            operator.save()
            #remove associated stuff with TO TODO
            messages.success(self.request, 'Tour operator deleted')
            return redirect('backend:admin_tour_operator')

        #PAGINATION
        form = TourOperatorFilterForm(self.request.GET or None)
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
            context['form'] = TourOperatorFilterForm()
        tour_operators = TourOperator.objects.filter(draft=False).filter(date_deleted__isnull=True)
        # filter logic
        if 'form' in kwargs and kwargs['form']:
            name = kwargs['form'].cleaned_data.get('name')
            if name:
                tour_operators = tour_operators.filter(name__lower__icontains=name.lower())
            order_by = kwargs['form'].cleaned_data.get('order_by')
            if order_by:
                tour_operators = tour_operators.order_by(order_by)
            
        # sort
        #sort = self.request.GET.get('sort', '')
        #how = self.request.GET.get('how', '')
        #if sort:
        #    tour_operators = tour_operators.order_by(how + sort)

        # page logic
        page = self.request.GET.get('page', 1)
        paginator = Paginator(tour_operators, 100)
        try:
            context['paginator'] = paginator.page(page)
        except PageNotAnInteger:
            context['paginator'] = paginator.page(1)
        except EmptyPage:
            context['paginator'] = paginator.page(paginator.num_pages)
        # to users
        to_users = {}
        for to in context['paginator']:
            to_user = to.profiles.first()
            if to_user:
                to_users[to.pk] = to_user.pk
        context['tour_operators_users'] = to_users
        #context['sort'] = sort
        #context['how'] = how
        return context

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
            photos = Photo.objects.filter(draft=False, date_deleted__isnull=True, park_review=review)
            self.template_name = 'backend/admin/open_park_review.html'


        if self.kwargs.get('tour_operator_review_pk') and not 'form' in context:
            review = TourOperatorReview.objects.get(pk=self.kwargs.get('tour_operator_review_pk'))
            context['form'] = TourOperatorReviewForm(instance=review)
            context['what'] = review.tour_operator
            context['title'] = 'Tour operator'
            self.template_name = 'backend/admin/open_tour_operator_review.html'
            temp = get_template('operators/tour_operator_includes/tour_reviews_cards.html')
            result = temp.render({'tour_reviews': [review], 'tour': review.tour_operator, 'focused': True})
            context['review_focus'] = result
            photos = Photo.objects.filter(draft=False, date_deleted__isnull=True, tour_operator_review=review)
        context['review'] = review
        context['photos'] = photos
        return context


class AdminArticleChangeView(AdminRequiredLoginView, TemplateView):
    template_name = "backend/admin/article.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = Article.objects.get(slug=self.kwargs.get('slug'))
        form = ArticleForm(instance=article)
        context['form'] = form
        return context


