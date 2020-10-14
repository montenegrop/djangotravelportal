from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from backend.forms import TourOperatorFilterForm
from operators.models import TourOperator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from django.shortcuts import redirect

class AdminRequiredLoginView(UserPassesTestMixin, LoginRequiredMixin):

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['disable_footer'] = True
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
