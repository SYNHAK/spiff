from django import forms
from django.contrib.auth.models import User
import models
from spiff.events.fields import JqSplitDateTimeField

class RankForm(forms.ModelForm):
  class Meta:
    model = User
    fields = ['groups']

class DueForm(forms.ModelForm):
  created = JqSplitDateTimeField()
  class Meta:
    model = models.DuePayment
    fields = ['value', 'created', 'rank', 'method']

class UserForm(forms.Form):
  email = forms.EmailField()
  firstName = forms.CharField()
  lastName = forms.CharField()
  tagline = forms.CharField(required=False)
  hidden = forms.BooleanField(required=False)

  def __init__(self, *args, **kwargs):
    instance = kwargs.pop('instance', 0)
    super(UserForm, self).__init__(*args, **kwargs)
    if instance:
      self.fields['email'].initial = instance.email
      self.fields['firstName'].initial = instance.first_name
      self.fields['lastName'].initial = instance.last_name
      self.fields['tagline'].initial = instance.member.tagline
      self.fields['hidden'].initial = instance.member.hidden

class ProfileForm(forms.Form):
  def __init__(self, *args, **kwargs):
    fields = kwargs.pop('fields', 0)
    values = kwargs.pop('values', 0)
    super(ProfileForm, self).__init__(*args, **kwargs)
    if fields:
      for field in fields:
        v = None
        if values:
          for value in values:
            if value.field.id == field.id:
              v = value
              break
        if v:
          self.fields['profile_%s'%field.id] = forms.CharField(label=field.name,
              help_text=field.description, initial=v.value,
              required=field.required)
        else:
          self.fields['profile_%s'%field.id] = forms.CharField(label=field.name,
              help_text=field.description, required=field.required)

  def fieldValue(self, field):
    return self.cleaned_data['profile_%s'%field.id]

class PaymentForm(forms.Form):
  MONTHS = map(lambda x:(x, x), range(1, 13))
  YEARS = map(lambda x:(x, x), range(2012, 2026))
  card = forms.CharField(label="Card Number")
  month = forms.ChoiceField(choices=MONTHS, label='Expiration Month')
  year = forms.ChoiceField(choices=YEARS, label='Expiration Year')
  cvc = forms.IntegerField(label='CVC', help_text='Three digits found on back of card')
