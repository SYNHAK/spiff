from django import forms
import models

class EventForm(forms.ModelForm):
  class Meta:
    model = models.Event
    fields = ('start', 'end', 'name', 'description')

class ReserveResourceForm(forms.Form):
  def __init__(self, *args, **kwargs):
    resources = kwargs.pop('resources', [])
    super(ReserveResourceForm, self).__init__(*args, **kwargs)
    for resource in resources:
      self.fields['resource_%d'%resource.id] = forms.BooleanField(label=resource.name, required=False)

  def resourceIsSelected(self, resource):
    return self.cleaned_data['resource_%d'%resource.id] == True
