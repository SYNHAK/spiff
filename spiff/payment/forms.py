from django import forms
from models import Payment
from spiff.events.fields import JqSplitDateTimeField

class PaymentForm(forms.Form):
  MONTHS = map(lambda x:(x, x), range(1, 13))
  YEARS = map(lambda x:(x, x), range(2012, 2026))
  card = forms.CharField(label="Card Number")
  month = forms.ChoiceField(choices=MONTHS, label='Expiration Month')
  year = forms.ChoiceField(choices=YEARS, label='Expiration Year')
  cvc = forms.IntegerField(label='CVC', help_text='Three digits found on back of card')

class AddPaymentForm(forms.ModelForm):
  class Meta:
    model = Payment
    fields = ['user', 'value', 'created', 'method']

  created = JqSplitDateTimeField()
