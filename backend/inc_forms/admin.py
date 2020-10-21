import datetime
from django import forms

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



class MemberFilterForm(forms.Form):
    ORDER_BY_CHOICES = (
        ('-username', 'Username'),
        ('username', 'Username reverse'),
    )
    search_by = forms.CharField(widget=forms.TextInput(), required=False)
    order_by = forms.ChoiceField(
        choices=ORDER_BY_CHOICES,
        label='Order by',
        help_text=''
    )
