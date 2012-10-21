from django import forms
from spiff.membership.forms import UserForm

class RegistrationForm(UserForm):
  username = forms.CharField()
  password = forms.CharField(widget=forms.PasswordInput)
  password_confirm = forms.CharField(widget=forms.PasswordInput)

class SearchForm(forms.Form):
  query = forms.CharField(label='')
