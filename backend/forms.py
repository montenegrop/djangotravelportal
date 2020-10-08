import datetime
from django import forms
from places.models import Country, CountryIndex, Park, Language, Activity, Animal
from operators.models import TourOperator, Itinerary, ItineraryType
from operators.models import ItineraryFocusType
from places.models import Currency
from operators.models import Month, ItineraryInclusion, ItineraryExclusion
from users.models import UserProfile, User
from crispy_forms.helper import FormHelper
from reviews.models import AbstractReview, ParkReview, TourOperatorReview
from crispy_forms.layout import Layout, Fieldset, Field
from blog.models import Article
from post_office.models import EmailTemplate
from core.forms import MyCheckboxSelectMultiple, MySelectDateWidget
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils import timezone


class TestEmailForm(forms.Form):
    email_to = forms.CharField(required=True)
    template = forms.ModelChoiceField(
        required=True, 
        queryset=EmailTemplate.objects.all().order_by('name')
        )

class ArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = '__all__'



from django.forms import ModelMultipleChoiceField

class ActivitiesMultipleChoiceField(ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return obj.name_short



class ParksMultipleChoiceField(ModelMultipleChoiceField):

    def label_from_instance(self, obj):
        return obj.name_short

class ParkReviewForm(forms.ModelForm):
    animals = forms.ModelMultipleChoiceField(
        queryset=Animal.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=False)
    activities =  ActivitiesMultipleChoiceField(
        queryset=Activity.objects.all().order_by('name_short'),
        widget=forms.CheckboxSelectMultiple,
        required=False)
    friend_recommend = forms.BooleanField(required=False)
    overall_rating = forms.IntegerField()
    quality_wildlife_rating = forms.IntegerField()
    quality_lodging_rating = forms.IntegerField()
    crowdedness_rating = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'rating'}))
    book_lodging = forms.BooleanField(required=False)

    

    content = forms.CharField(widget=forms.Textarea(attrs={'rows': '20'}),required=True)

    class Meta:
        model = ParkReview
        fields = ('title','content','animals','activities',
        'friend_recommend','overall_rating',
        'quality_wildlife_rating','quality_lodging_rating',
        'crowdedness_rating','book_lodging',
        'status', 'reject_reason')

from post_office.models import EmailTemplate
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class EmailTemplateForm(forms.ModelForm):
    html_content = forms.CharField(widget=CKEditorUploadingWidget())
    class Meta:
        model = EmailTemplate
        fields = ('name','subject','description','content','html_content',)

class TourOperatorReviewForm(forms.ModelForm):
    parks = ParksMultipleChoiceField(
        queryset=Park.objects.all().order_by('name_short'),
        widget=forms.CheckboxSelectMultiple)
    animals = forms.ModelMultipleChoiceField(
        queryset=Animal.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=False)
    activities = ActivitiesMultipleChoiceField(
        queryset=Activity.objects.all().order_by('name_short'),
        widget=forms.CheckboxSelectMultiple,
        required=False)
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': '20'}),required=True)

    friend_recommend = forms.BooleanField(required=False)
    overall_rating = forms.IntegerField()
    meet_and_greet_rating = forms.IntegerField()
    responsiveness_rating = forms.IntegerField()
    safari_quality_rating = forms.IntegerField()
    itinerary_quality_rating = forms.IntegerField()
    overall_rating = forms.IntegerField()
    vehicle_rating = forms.IntegerField()


    class Meta:
        model = TourOperatorReview
        fields = ('title','content','animals',
        'activities','parks',
        'friend_recommend', 
        'overall_rating',
        'meet_and_greet_rating','responsiveness_rating',
        'safari_quality_rating','itinerary_quality_rating',
        'overall_rating','vehicle_rating',
        'status', 'reject_reason',)




class TourOperatorFilterForm(forms.Form):
    ORDER_BY_CHOICES = (
        ('-name', 'Name'),
        ('name', 'Name reverse'),
        ('-yas_score', 'YASScore'),
        ('yas_score', 'YASScore reverse'),
    )
    name = forms.CharField(widget=forms.TextInput(), required=False)
    order_by = forms.ChoiceField(
        choices=ORDER_BY_CHOICES,
        label='Order by',
        help_text=''
    )



class QuoteRequestFilterForm(forms.Form):
    tour_operator = forms.ModelChoiceField(
        required=False, 
        widget=forms.Select(attrs={'class': "select2"}),
        queryset=TourOperator.objects.all().order_by('name')
        )
    country_index = forms.ModelChoiceField(
        required=False, 
        widget=forms.Select(attrs={'class': "select2"}),
        queryset=CountryIndex.objects.all().order_by('name')
    )
    date_range = forms.CharField(widget=forms.TextInput(attrs={'class':'daterange'}), required=False)
    only_unseen = forms.BooleanField(required=False)


class YASScoreForm(forms.Form):
    country = forms.ModelChoiceField(
        queryset=CountryIndex.objects.all().order_by('name'),
        required=False,
        label='Change country')

class TourPackageForm(forms.ModelForm):
    itinerary_type = forms.ModelChoiceField(
        queryset=ItineraryType.objects.all(),
        required=True,
        empty_label=None,
        widget=forms.RadioSelect,
        label='What type of itinerary is this?')

    country_indexes = forms.ModelMultipleChoiceField(
        queryset=CountryIndex.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        label='Which countries will the itinerary visit?')

    safari_focus_activity = forms.ModelChoiceField(
        required=True,
        queryset=None,
        empty_label=None,
        widget=forms.RadioSelect(attrs={'class': 'col-4', 'flat_attrs': 'col-4'}),
        label='Safari: what is the primary focus?')

    non_safari_focus_activity = forms.ModelChoiceField(
        required=True,
        queryset=None,
        label='Safari: what is the secondary focus?')

    secondary_focus_activity = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=None,
        label='What are the highlights? <span class="text-warning">New feature! Showcase more aspects of your tours and reach your target audience.</span>')

    parks = forms.ModelMultipleChoiceField(
        queryset=Park.objects.all().order_by('name'),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        label='Which park(s) does this itinerary include?')

    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'maxlen', 'maxlength': 100}),
        required=True,
        label='Tour package name',
        help_text='<b>Example:</b> Serengeti, Tarangire and Lake Manyara camping safari. <br>*Don’t include number of days in title. It’s automatically pulled from this form.')

    min_price = forms.CharField(
        label='Min price',
        required=True
    )
    max_price = forms.CharField(
        widget=forms.TextInput(),
        label='Max price',
        required=False
    )

    title_short = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'maxlen', 'maxlength': 25}),
        required=True,
        label='Short title for search results',
        help_text='<b>Example:</b> Big five safari')

    # header = forms.CharField(
    #    widget=forms.Textarea(attrs={'rows':'3','class':'maxlen','maxlength':60}),
    #    required=True,
    #    label='Header',
    #    help_text='This will appear at the top of the page (above your itinerary fact sheet. Use this to grab our members attention)')

    summary = forms.CharField(
        widget=forms.Textarea(attrs={'rows': '3', 'class': 'maxlen', 'maxlength': 1000}),
        required=True,
        label='Summary',
        help_text='')

    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': '4', 'class': 'maxlen', 'maxlength': 100}),
        required=True,
        label='Day by day itinerary description',
        help_text='<b>Please note:</b> Any formatting outside the YAS guidelines will be removed. For example: colored text or links will be automatically removed')

    currency = forms.ModelChoiceField(
        queryset=Currency.objects.all(),
        label='Currency')

    days = forms.ChoiceField(
        choices=[(i, str(i) + (' day' if i == 1 else ' days')) for i in range(1, 19)],
        label='Length of safari',
        help_text=''
    )

    flight = forms.TypedChoiceField(
        coerce=lambda x: x == 'Yes',
        choices=((False, 'No'), (True, 'Yes')),
        widget=forms.RadioSelect,
        label='Do you do include internal flights?'
    )

    single_supplement = forms.TypedChoiceField(
        coerce=lambda x: x == 'Yes',
        choices=((False, 'No'), (True, 'Yes')),
        widget=forms.RadioSelect,
        label='Do you charge a single supplement?'
    )
    single_supplement_price = forms.CharField(
        required=True,
        label='Single suplement price',
        help_text='')

    inclusions = forms.ModelMultipleChoiceField(
        required=True,
        widget=forms.CheckboxSelectMultiple(attrs={'data-name': 'name'}),
        queryset=ItineraryInclusion.objects.all().order_by('name'),
        label="What's included? Select all that apply")

    other_inclusion = forms.CheckboxInput()

    other_inclusion_text = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'maxlen', 'maxlength': 50, 'placeholder': 'Other'}),
        required=True,
        label=False,
        help_text='')

    exclusions = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'data-name': 'name'}),
        queryset=ItineraryExclusion.objects.all().order_by('name'),
        label="What's excluded? Select all that apply")

    other_exclusion = forms.CheckboxInput()

    other_exclusion_text = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'maxlen', 'maxlength': 50, 'placeholder': 'Other'}),
        required=True,
        label=False,
        help_text='')


    months = forms.ModelMultipleChoiceField(
        required=True,
        widget=forms.CheckboxSelectMultiple,
        queryset=Month.objects.all(),
        label='Best time to visit')

    image = forms.ImageField(
        required=True,
        widget=forms.FileInput,
        label='Add an itinerary photo',
        help_text='Please select a photo that is high quality (800x600) and representative of the tour. Landscape orientation works best'
    )
    accept_terms = forms.BooleanField(
        label='Accept the terms',
        help_text='By using this photo, I claim I am the owner of these photos and you agree with our <a href="/terms-of-use/" target="_blank">terms of use</a>'
    )


    class Meta:
        model = Itinerary
        fields = '__all__'
        exclude = ('slug', 'date_created',)

    def __init__(self, tour_operator=None, *args, **kwargs):
        super(TourPackageForm, self).__init__(*args, **kwargs)
        if tour_operator:
            self.fields['country_indexes'].queryset = tour_operator.country_indexes.all()
        usd, _ = Currency.objects.get_or_create(code='USD')
        self.fields['currency'].initial = usd
        self.fields['safari_focus_activity'].queryset = ItineraryFocusType.objects.get_or_create(name='Primary').activities.filter(enabled=True).order_by('name'),
        self.fields['non_safari_focus_activity'].queryset = ItineraryFocusType.objects.get_or_create(name='Non safari').activities.filter(enabled=True).order_by('name')
        self.fields['secondary_focus_activity'].queryset = ItineraryFocusType.objects.get_or_create(name='Secondary').activities.filter(enabled=True).order_by('name')

class CompanyInfoForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': True,'data-rule-required':"true"}), 
        required=True)
    website = forms.CharField(widget=forms.TextInput(attrs={'readonly': True,'class':'validUrl', 'placeholder':'yourwebsite.com'}),required=True)
    email = forms.CharField(widget=forms.TextInput(attrs={'readonly': True,'class':'email'}),required=True)
    facebook = forms.CharField(widget=forms.TextInput(attrs={'class':'validUrl', 'placeholder':'facebook.com/yourcompany'}), required=False)
    twitter = forms.CharField(widget=forms.TextInput(attrs={'class':'validUrl', 'placeholder':'twitter.com/yourcompany'}), required=False)
    blog = forms.CharField(widget=forms.TextInput(attrs={'class':'validUrl', 'placeholder':'yourblog.com'}), required=False)
    linkedin = forms.CharField(widget=forms.TextInput(attrs={'class':'validUrl', 'placeholder':'linkedin.com/in/yourcompany'}), required=False)
    whatsapp = forms.CharField(widget=forms.NumberInput(attrs={'class':'phone', 'maxlength':14, 'placeholder':''}), required=False)
    telephone = forms.CharField(widget=forms.NumberInput(attrs={'class':'phone', 'maxlength':14, 'placeholder':''}), required=False)
    now = datetime.datetime.now()

    startup_date = forms.DateField(required=True,
        initial=timezone.now(),
        widget=forms.SelectDateWidget(years=range(1980, now.year + 1),
        #empty_label=(u'month', u'day',u'year'),
        attrs={'style': 'display: inline-block; width: 33%;'}))
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'maxlen','maxlength': 1000}),
        required=True)
    vehicle_description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'maxlen', 'maxlength': 600}),
        required=True)
    country_indexes = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'countries'}),
        queryset=CountryIndex.objects.all(),
        label='Operating in',
        required=True,
    )
    parks = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'parks'}),
        queryset=Park.objects.all(),
        label='Parks and game reserves you visit',
        required=True,
    )
    languages = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        queryset=Language.objects.all().order_by('name'),
        label='Languages spoken',
        required=False,
    )
    group_safari = forms.BooleanField(required=False)
    book_attraction = forms.BooleanField(required=False)
    tailored_safari = forms.BooleanField(required=False)
    international_flight = forms.BooleanField(required=False)

    class Meta:
        model = TourOperator
        fields = '__all__'
        exclude = ('slug', 'date_created', 'yas_modifier', 'yas_score','reviews_count', 'average_rating','packages_count','quote_request_count','parks_count', 'date_deleted', 'first_kudu_email', 'last_review_date', 'date_modified_yas_score')

    def clean_startup_date(self):
        startup_date = self.cleaned_data['startup_date']
        if startup_date > datetime.date.today():
            raise forms.ValidationError("Startup date must be in the past")
        return startup_date


class MemberInfoProfileForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'class': 'maxlen', 'maxlength': 1000}))
    facebook = forms.URLField(required=False, help_text='example: https://www.facebook.com/yourafricansafari')
    twitter = forms.URLField(required=False)
    website = forms.URLField(required=False)
    linkedin = forms.URLField(required=False)
    pinterest = forms.URLField(required=False)
    youtube = forms.URLField(required=False)

    SAFARI_COUNT = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
        (7, '7'),
        (8, '8'),
        (9, '9'),
        (10, '10+'),
    )

    safari_count = forms.ChoiceField(choices=SAFARI_COUNT, widget=forms.Select(attrs={'class': 'w-auto'}), label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

    class Meta:
        model = UserProfile
        fields = '__all__'
        exclude = (
            'slug', 'date_created', 'gender', 'user', 'tour_operator', 'luxury_level', 'user_type', 'animals_seen',
            'activities_enjoy', 'countries_visited', 'reviews_count', 'kudus_count')
        labels = {'country': 'Residence', 'description': ''}


class MemberInfoUserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

    first_name = forms.CharField(label='First name')
    password = forms.CharField(required=False, widget=forms.PasswordInput)
    email = forms.CharField(widget=forms.TextInput(attrs={'readonly': True}), required=True)

    class Meta:
        model = User
        fields = '__all__'
        exclude = ('slug', 'username', 'date_joined', 'password', 'is_active', 'is_staff', 'is_superuser')
