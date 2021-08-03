from django import forms
from django.contrib.auth.forms import UserCreationForm
# from cuser.forms import UserCreationFormForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import LocationHistory

'''
class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username","email","password1","password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
'''


class HistUserForm(forms.Form):
    email = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100)

    def __init__(self, *args, **kwargs):

        super(HistUserForm, self).__init__(*args, **kwargs)

        extra_fields = kwargs.pop('extra', 0)

        if int(extra_fields) == 1:
            # Text
            self.fields["recovery_mail"] = forms.CharField(label="recovery_mail", required=False)
        elif int(extra_fields) == 2:
            # Number
            self.fields["recovery_phone"] = forms.CharField(label="recovery_phone", required=False)



# class HistUserForm(forms.Form):
#     email = forms.CharField(max_length=100)
#     password = forms.CharField(max_length=100)
#     recovery_mail = forms.CharField(max_length=100)
#     recovery_phone = forms.CharField(max_length=100)


class LocHistFileForm(forms.ModelForm):
    class Meta:
        model = LocationHistory
        fields = ('zip_file',)

        labels = {
            "zip_file": "Google Location History ZIP File"
        }
        help_text = {
            "zip_file": "Only zip files accepted"
        }
        widgets = {
            "zip_file": forms.FileInput(attrs={'accept': 'application/zip'}),
        }
