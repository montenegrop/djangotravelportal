from django.contrib import admin
from reviews.models import SafariType, ParkReview, TourOperatorReview, KilimanjaroParkReview
from django import forms
from django.db import models

admin.site.register(SafariType)


class ParkReviewAdminForm(forms.ModelForm):
    class Meta:
        model = ParkReview
        fields = '__all__'
        widgets = {
            'quality_wildlife_rating': forms.NumberInput(attrs={'class': 'vIntegerField star'}),
        }


@admin.register(ParkReview)
class ParkReviewAdmin(admin.ModelAdmin):
    form = ParkReviewAdminForm
    prepopulated_fields = {'slug': ('title',)}
    exclude = ['user']
    list_display = ['pk', 'title', 'park', 'user']

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Only set added_by during the first save.
            obj.user = request.user
        super().save_model(request, obj, form, change)


class KilimanjaroParkReviewAdminForm(forms.ModelForm):
    class Meta:
        model = ParkReview
        fields = '__all__'
        widgets = {
            'quality_wildlife_rating': forms.NumberInput(attrs={'class': 'vIntegerField star'}),
        }


@admin.register(KilimanjaroParkReview)
class KilimanjaroParkReviewAdmin(admin.ModelAdmin):
    form = KilimanjaroParkReviewAdminForm
    prepopulated_fields = {'slug': ('title',)}
    exclude = ['user']
    list_display = ['pk', 'title', 'user']

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Only set added_by during the first save.
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(TourOperatorReview)
class TourOperatorReviewAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    exclude = ['user']
    list_display = ['pk', 'title', 'tour_operator']
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Only set added_by during the first save.
            obj.user = request.user
        super().save_model(request, obj, form, change)


