from django import forms
from django.contrib.auth.models import User
import models
import fields

class EventForm(forms.ModelForm):
  class Meta:
    fields = ['start', 'end', 'name', 'description']
  start = fields.JqSplitDateTimeField()
  end = fields.JqSplitDateTimeField()
  name = forms.CharField()
  description = forms.CharField(widget=forms.Textarea)

class AddOrganizerForm(forms.Form):
  organizer = forms.ModelChoiceField(queryset=User.objects.all())

class ReserveResourceForm(forms.Form):
  def __init__(self, *args, **kwargs):
    resources = kwargs.pop('resources', [])
    super(ReserveResourceForm, self).__init__(*args, **kwargs)
    for resource in resources:
      self.fields['resource_%d'%resource.id] = forms.BooleanField(label=resource.name, required=False)

  def resourceIsSelected(self, resource):
    return self.cleaned_data['resource_%d'%resource.id] == True
