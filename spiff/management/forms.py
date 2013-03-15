from django import forms
from spiff.membership.forms import UserForm
from django.contrib.auth.models import User

class RegistrationForm(UserForm):
  username = forms.CharField(required=False)

class UserSelectionForm(forms.Form):
  user = forms.ModelChoiceField(queryset=User.objects.all())
