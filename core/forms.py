from django import forms    
from django.contrib.auth.forms import AuthenticationForm, UsernameField

class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        label='Email',
        widget=forms.TextInput(attrs={'autofocus': True,"autocapitalize":"off"})
    )


class MySelectDateWidget(forms.SelectDateWidget):

    def get_context(self, name, value, attrs):
        old_state = self.is_required
        self.is_required = False
        context = super(MySelectDateWidget, self).get_context(name, value, attrs)
        self.is_required = old_state
        return context

class MySelect(forms.Select):

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super(forms.Select, self).create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            for k,attr in self.attrs.items():
                # if it has a data attr in it
                if k[:4] == 'data':
                    #instantiate a new object and add the data attr to the option
                    current_object = self.choices.queryset.model.objects.get(pk=value)
                    option['attrs'].update({
                        k: getattr(current_object, attr)
                    })
        return option


class MyCheckboxSelectMultiple(forms.CheckboxSelectMultiple):

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super(forms.CheckboxSelectMultiple, self).create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            for k,attr in self.attrs.items():
                # if it has a data attr in it
                if k[:4] == 'data':
                    #instantiate a new object and add the data attr to the option
                    current_object = self.choices.queryset.model.objects.get(pk=value)
                    option['attrs'].update({
                        k: getattr(current_object, attr)
                    })
        return option