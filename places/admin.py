from django.contrib import admin
from places.models import *
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from froala_editor.widgets import FroalaEditor


class AnimalAdminForm(forms.ModelForm):
    description = forms.CharField(widget=FroalaEditor())

    class Meta:
        model = Animal
        fields = '__all__'


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    form = AnimalAdminForm


@admin.register(CountryIndex)
class CountryIndexAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

    class Meta:
        model = CountryIndex
        widgets = {'activities': forms.CheckboxSelectMultiple}


class ActivityAdminForm(forms.ModelForm):
    description = forms.CharField(widget=FroalaEditor())

    class Meta:
        model = Activity
        fields = '__all__'

class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code','symbol', 'usd_exchange_rate', 'date_modified']

    class Meta:
        model = Currency
        fields = '__all__'

admin.site.register(Currency, CurrencyAdmin)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    form = ActivityAdminForm
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
    list_display = ['name','name_short', 'name_old', 'activity_level', 'activity_level_name','get_focus_type','has_image','is_enabled','date_modified']
    search_fields = ['name', 'name_short', 'activity_level']

    def is_enabled(self, obj):
        if obj.enabled:
            return 'yes'
        return 'no'

    def activity_level_name(self, obj):
        if obj.enabled:
            return 'yes'
        return 'no'

    def has_image(self, obj):
        if obj.image:
            return 'yes'
        return 'no'

    def get_focus_type(self, obj):
        return "\n".join([p.name     for p in obj.focus_type.all()])



from import_export.admin import ImportExportModelAdmin

@admin.register(Park)
class ParkAdmin(ImportExportModelAdmin):
    list_display = ['name','safari_focus_activity', 'get_secondary']
    prepopulated_fields = {'slug': ('name',)}

    def get_secondary(self, obj):
        return ",".join([p.name for p in obj.secondary_focus_activity.all()])


admin.site.register(Plug)
admin.site.register(Vaccination)
admin.site.register(Continent)

admin.site.register(Country)
admin.site.register(Language)
admin.site.register(Airline)
