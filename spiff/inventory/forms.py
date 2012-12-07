from django import forms
import models

class TrainingForm(forms.Form):
  rank = forms.IntegerField()
  comments = forms.CharField()

  def __init__(self, *args, **kwargs):
    instance = kwargs.pop('instance', 0)
    super(TrainingForm, self).__init__(*args, **kwargs)
    if instance:
      self.fields['rank'].initial = instance.rank
      self.fields['comments'].initial = instance.comments

class MetadataForm(forms.ModelForm):
  class Meta:
    model = models.Metadata
    fields = ['name', 'value', 'type']
