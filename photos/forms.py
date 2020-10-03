from django import forms
from .models import Comment, Photo, Tag
from places.models import CountryIndex, Activity, Animal, Park
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Div, HTML
from tags_input.fields import TagsInputField


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('user', 'comment')


class PhotoSearchForm(forms.Form):
    country = forms.ModelChoiceField(queryset=CountryIndex.objects.all())
    park = forms.ModelChoiceField(queryset=Park.objects.all())
    animal = forms.ModelChoiceField(queryset=Animal.objects.all().order_by('name'))
    activity = forms.ModelChoiceField(queryset=Activity.objects.all())


class PhotoTagsForm(forms.ModelForm):

    country_index = forms.ModelChoiceField(queryset=CountryIndex.objects.all(), required=False, label="Where was this picture taken?")
    park = forms.ModelChoiceField(queryset=Park.objects.all(), required=False, label="Park / game reserve?")
    activity = forms.ModelChoiceField(queryset=Activity.objects.filter(activity_type="SAFARI"), required=False, label="What were you doing?")
    animals = forms.ModelMultipleChoiceField(
            label="Any animals in the photo?",
            required=False,
            widget=forms.SelectMultiple(attrs={'class': "select2"}),
            queryset=Animal.objects.all().order_by('name'),
            )

    tags = TagsInputField(queryset=Tag.objects.all(), label="Additional tags (example: sunset, jeep)", required=False)


    class Meta:
        model = Photo
        fields = ('country_index', 'park', 'activity', 'animals', 'tags')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.data.get('country_index',''):
            self.fields['park'].queryset = Park.objects.filter(country_indexes__id=self.data['country_index'])
        else:
            if self.instance.country_index:
                self.fields['park'].queryset = Park.objects.filter(country_indexes__id=self.instance.country_index.id)
            else:
                self.fields['park'].queryset = Park.objects.none()
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    Div(
                        'country_index',
                        css_class="col-12 col-md-6"
                    ),
                    Div(
                        'park',
                        css_class="col-12 col-md-6"
                    ),

                    css_class="row"
                ),
                Div(
                    Div(
                        'activity',
                        css_class="col-12 col-md-6"
                    ),

                    css_class="row"
                ),
                Div(
                    Div(
                        'animals',
                        css_class="col-12"
                    ),

                    css_class="row"
                ),
                Div(
                    Div(
                        'tags',
                        css_class="col-12"
                    ),

                    css_class="row"
                ),
                css_class="container"
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white'),
                HTML('<a class="cancel" id="cancel_button">Cancel</a>')
            )
        )

