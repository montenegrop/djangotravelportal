from django.views.generic import TemplateView
from django.shortcuts import render

class Custom404(TemplateView):
    template_name = "yas/404.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class Custom403(TemplateView):
    template_name = "yas/403.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def custom500(request):
    template_name = "yas/500.html"
    return render(request, template_name,)
