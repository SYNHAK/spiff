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

class ProfileForm(forms.Form):
  def __init__(self, *args, **kwargs):
    fields = kwargs.pop('fields', 0)
    super(ProfileForm, self).__init__(*args, **kwargs)
    for field in fields:
      self.fields['profile_%s'%field.id] = forms.CharField(label=field.name,
          help_text=field.description)

  def fieldValue(self, field):
    return self.cleaned_data['profile_%s'%field.id]
