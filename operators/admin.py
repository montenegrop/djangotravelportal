from django.contrib import admin
from operators.models import TourOperator, Itinerary, QuoteRequest
from operators.models import ItineraryActivity,ItineraryFocusType
from import_export.admin import ImportExportModelAdmin
from operators.models import ItineraryInclusion, ItineraryExclusion, YASScore

@admin.register(TourOperator)
class TourOperatorAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_display = ['name', 'yas_score','date_modified_yas_score','date_modified']

from django.forms import CheckboxSelectMultiple
from django.db import models

@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ['title', 'activity_level','activity_level_name','get_parks','safari_focus_activity', 'get_secondary']
    search_fields = ['title', 'activity_level','activity_level_name']
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    def get_secondary(self, obj):
        return ",".join([p.name_short for p in obj.secondary_focus_activity.all()])
    def get_parks(self, obj):
        return ",".join([p.name_short for p in obj.parks.all()])


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_created', 'itinerary', 'tour_operator']
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

admin.site.register(ItineraryFocusType)


@admin.register(ItineraryInclusion)
class ItineraryInclusionAdmin(ImportExportModelAdmin):
    list_display = ['name','explanation','date_modified']
    search_fields = ['name', 'explanation']
    ordering = ('name',)

@admin.register(YASScore)
class YASScoreAdmin(ImportExportModelAdmin):
    list_display = ['tour_operator','country_index','yas_score', 'date_modified']
    search_fields = ['tour_operator', 'country_index']
    ordering = ('tour_operator',)

@admin.register(ItineraryExclusion)
class ItineraryExclusionAdmin(ImportExportModelAdmin):
    list_display = ['name','explanation','date_modified']
    search_fields = ['name', 'explanation']
    ordering = ('name',)


#@admin.register(ItineraryActivity)
#class ItineraryActivityAdmin(ImportExportModelAdmin):
#    list_display = ['name','name_short','activity_level','get_focus_type','date_modified']
#    search_fields = ['name', 'name_short', 'activity_level']
#    ordering = ('name',)
#    def get_focus_type(self, obj):
#        return "\n".join([p.name     for p in obj.focus_type.all()])

