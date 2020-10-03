from django.forms import ModelForm, DateTimeInput
from .models import UserProfile
from django import forms
from django.contrib.admin import widgets
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['date_of_birth', 'country', 'badges', 'screen_name',
                  'gender', 'luxury_level', 'countries_visited']


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, required=True, help_text='Required')
    last_name = forms.CharField(
        max_length=30, required=True, help_text='Optional.')
    screen_name = forms.CharField(
        max_length=30, required=True, help_text='Optional.')
    email = forms.EmailField(max_length=254, required=True,
                             help_text='Required. Inform a valid email address.')
    password1 = forms.CharField(
        max_length=30, required=True, help_text='Optional.')
    password2 = forms.CharField(
        max_length=30, required=True, help_text='Optional.')
    terms = forms.BooleanField(required=True, help_text='Optional.')
    #recaptcha = ReCaptchaField(widget=ReCaptchaV3)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'screen_name',
                  'email', 'password1', 'password2', 'username']
