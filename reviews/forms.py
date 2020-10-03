from django import forms
from django.db import models
from .models import ParkReview, TourOperatorReview, KilimanjaroParkReview
from places.models import Country
from django.core.validators import EMPTY_VALUES


class ParkReviewForm(forms.ModelForm):
    title = forms.CharField(max_length=300, required=True, help_text='Optional.')
    content = forms.CharField(min_length=150, required=True, help_text='Optional.')
    friend_recommend = forms.BooleanField(required=False)
    book_lodging = forms.BooleanField(required=False)
    visit_date = forms.DateField()
    days_booked = forms.IntegerField()

    quality_wildlife_rating = forms.IntegerField(min_value=0, max_value=5)
    quality_lodging_rating = forms.IntegerField(min_value=0, max_value=5)
    crowdedness_rating = forms.IntegerField(min_value=0, max_value=5)
    overall_rating = forms.IntegerField(min_value=0, max_value=5)
    pearls_of_wisdom = forms.CharField(max_length=200, required=False, help_text='Optional.')


    class Meta:
        model = ParkReview
        exclude = ['i_certify_these_photos', 'like_upload_photos']
        fields = (
            'title',
            'content',
            'friend_recommend',
            'book_lodging',
            'visit_date',
            'days_booked',
            'quality_wildlife_rating',
            'quality_lodging_rating',
            'crowdedness_rating',
            'overall_rating',
            'pearls_of_wisdom',
        )


class ParkKilimanjaroReviewForm(ParkReviewForm):
    reached_summit = forms.BooleanField(required=False)
    take_medications = forms.BooleanField(required=False)
    route_to_climb = forms.ChoiceField(choices=KilimanjaroParkReview.ROUTES_CHOICES, required=False)
    other_route_to_climb = forms.CharField(required=False, max_length=40)

    def clean(self):
        route_to_climb = self.cleaned_data.get('route_to_climb')
        other_route_to_climb = self.cleaned_data.get('other_route_to_climb')
        if route_to_climb is None and other_route_to_climb is None:
            self._errors['other_route_to_climb'] = self.error_class(['This field is required.'])
        return self.cleaned_data

    class Meta:
        model = KilimanjaroParkReview
        exclude = ['i_certify_these_photos', 'like_upload_photos']
        fields = (
            'title',
            'content',
            'friend_recommend',
            'book_lodging',
            'days_booked',
            'quality_wildlife_rating',
            'quality_lodging_rating',
            'crowdedness_rating',
            'overall_rating',
            'visit_date',
            'reached_summit',
            'take_medications',
            'route_to_climb',
            'other_route_to_climb',
            'pearls_of_wisdom'
        )

class TourOperatorReviewForm(forms.ModelForm):
    title = forms.CharField(max_length=300, required=True, help_text='Optional.')
    content = forms.CharField(min_length=150, required=True, help_text='Optional.')
    pearls_of_wisdom = forms.CharField(max_length=200, required=False, help_text='Optional.')
    friend_recommend = forms.BooleanField(required=False)
    vehicle_rating = forms.IntegerField(min_value=0, max_value=5)
    meet_and_greet_rating = forms.IntegerField(min_value=0, max_value=5)
    responsiveness_rating = forms.IntegerField(min_value=0, max_value=5)
    safari_quality_rating = forms.IntegerField(min_value=0, max_value=5)
    itinerary_quality_rating = forms.IntegerField(min_value=0, max_value=5)
    overall_rating = forms.IntegerField(min_value=0, max_value=5)
    days_booked = forms.CharField(max_length=200, required=False, help_text='Optional.')
    did_not_go = forms.BooleanField(required=False)
    find_out = forms.ChoiceField(choices=TourOperatorReview.FIND_OUT_CHOICES)
    find_out_website = forms.CharField(required=False)
    reached_summit = forms.BooleanField(required=False)
    take_medications = forms.BooleanField(required=False)
    route_to_climb = forms.ChoiceField(choices=KilimanjaroParkReview.ROUTES_CHOICES, required=False)
    other_route_to_climb = forms.CharField(max_length=40, required=False)
    start_date = forms.DateField(required=False)

    class Meta:
        model = TourOperatorReview
        fields = ('title', 'content', 'pearls_of_wisdom',  'friend_recommend', 'vehicle_rating', 'meet_and_greet_rating', 'responsiveness_rating', 'safari_quality_rating', 'itinerary_quality_rating', 'overall_rating', 'days_booked',  'did_not_go', 'find_out', 'find_out_website', 'reached_summit', 'take_medications', 'route_to_climb', 'other_route_to_climb', 'start_date')
