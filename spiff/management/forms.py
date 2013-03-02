from django import forms
from spiff.membership.forms import UserForm

class RegistrationForm(UserForm):
  username = forms.CharField(required=False)

