from django.contrib import admin
from analytics.models import Analytic

@admin.register(Analytic)
class AnalyticAdmin(admin.ModelAdmin):
    model = Analytic
    list_display = [field.name for field in Analytic._meta.get_fields()]
