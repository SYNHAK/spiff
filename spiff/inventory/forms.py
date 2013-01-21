from django import forms
import models

class AddResourceForm(forms.ModelForm):
  class Meta:
    model = models.Resource
    fields = ['name', 'trainable']

class CertificationForm(forms.ModelForm):
   class Meta:
    model = models.Certification
    fields = ['member', 'comment']

class MetadataForm(forms.ModelForm):
  class Meta:
    model = models.Metadata
    fields = ['name', 'value', 'type']
