from django import forms
from operators.models import QuoteRequest, ItineraryType
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, HTML
from places.models import CountryIndex
import datetime
from places.models import Country
from core.utils import add_months

class QuoteRequestForm(forms.ModelForm):
    name = forms.CharField(max_length=600, required=True, label='Please enter your full name')
    email = forms.EmailField(required=True, label='Enter your email')
    telephone = forms.CharField(required=False, label='Contact telephone (optional)')
    
    date_trip = forms.DateField(required=True, label='Estimated date of arrival?',widget=forms.SelectDateWidget())
    party_size = forms.ChoiceField(required=True, label='How many people in your party?', choices=
                                   (('', '-- Please select --'),
                                    ('1', '1'),
                                    ('2', '2'),
                                    ('3', '3'),
                                    ('4', '4'),
                                    ('5', '5'),
                                    ('6', '6'),
                                    ('7', '7'),
                                    ('8', '8'),
                                    ('9', '9'),
                                    ('10', '10'),
                                    ('11-15', '11-15'),
                                    ('15+', '15+')))
    days = forms.ChoiceField(required=True, label='How long do you want to visit (days)?',  choices=
                                   (('', '-- Please select --'),
                                    ('1', '1'),
                                    ('2', '2'),
                                    ('3', '3'),
                                    ('4', '4'),
                                    ('5', '5'),
                                    ('6', '6'),
                                    ('7', '7'),
                                    ('8', '8'),
                                    ('9', '9'),
                                    ('10', '10'),
                                    ('11', '11'),
                                    ('12', '12'),
                                    ('13', '13'),
                                    ('14', '14'),
                                    ('15', '15'),
                                    ('16', '16'),
                                    ('17', '17'),
                                    ('18', '18'),
                                    ('19', '19'),
                                   ))
    country_indexes = forms.ModelMultipleChoiceField(
            label="Where do you want to visit?",
            required=True,
            widget=forms.CheckboxSelectMultiple(attrs={'class':'country_indexes'}),
            queryset=CountryIndex.objects.all()
            )

    #country = forms.ModelChoiceField(
    #    queryset=Country.objects.all().order_by('name'),
    #    required=False,
    #    widget=forms.Select(attrs={'class': "select2"}),
    #    label='What country are you from?')

    additional_information = forms.CharField(required=False, 
    label="Additional information (Are there any parks you want to see or do you have special requirements?)", 
    widget=forms.Textarea(attrs={'rows':3}))

    def clean_date_trip(self):
        date_trip = self.cleaned_data['date_trip']
        if date_trip <= datetime.date.today():
            raise forms.ValidationError("Date of arrival must be in the future")
        return date_trip
    
    def __init__(self, *args, **kwargs):
        super(QuoteRequestForm, self).__init__(*args, **kwargs)
        self.fields['date_trip'].initial = add_months(datetime.datetime.now(), 1)


    class Meta:
        model = QuoteRequest
        fields = (
            'name',
            'email',
            'telephone',
            'itinerary_type',
            'date_trip',
            'days',
            'party_size',
            'country_indexes',
            'country',
            'additional_information'
        )

