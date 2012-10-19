from django import forms
from django.contrib.auth.models import User
import models

class UserForm(forms.Form):
  username = forms.CharField()
  password = forms.CharField(widget=forms.PasswordInput)
  password_confirm = forms.CharField(widget=forms.PasswordInput)
  email = forms.EmailField()

class MemberForm(forms.Form):
  firstName = forms.CharField()
  lastName = forms.CharField()
  birthday = forms.DateField()
