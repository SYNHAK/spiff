from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings
import stripe
from django.http import HttpResponseRedirect
from django.contrib import messages
import models
import forms
from django.shortcuts import render_to_response

def viewInvoice(request, invoiceID):
  invoice = models.Invoice.objects.get(pk=invoiceID)
  return render_to_response('payment/viewInvoice.html',
    {'invoice': invoice},
    context_instance=RequestContext(request))

def pay(request, invoiceID):
  invoice = models.Invoice.objects.get(pk=invoiceID)
  if request.method == 'POST':
    form = forms.PaymentForm(request.POST)
  else:
    form = forms.PaymentForm()
  balance = invoice.unpaidBalance
  if stripe.api_key == "":
    messages.error(request, "Stripe is not configured for this Spiff install.")
    return render_to_response('membership/pay.html',
      {'form': form, 'invoice': invoice},
      context_instance=RequestContext(request))
  if balance < 0.5:
    messages.error(request, "Your outstanding balance of $%d costs less than "
        "$0.50, which is too small for Stripe to process."%(balance))
    return render_to_response('payment/pay.html',
      {'form': form, 'invoice': invoice},
      context_instance=RequestContext(request))

  if form.is_valid():
    stripe.api_key = settings.STRIPE_KEY
    cardData = {}
    cardData['number'] = form.cleaned_data['card']
    cardData['exp_month'] = form.cleaned_data['month']
    cardData['exp_year'] = form.cleaned_data['year']
    cardData['cvc'] = form.cleaned_data['cvc']
    try:
      charge = stripe.Charge.create(
        amount = int(balance*100),
        currency = 'usd',
        card = cardData,
        description = 'Payment from %s for invoice %s'%(request.user.member.fullName, invoice.id)
      )
      payment = models.Payment.objects.create(
        user = request.user,
        value = balance,
        status = models.Payment.STATUS_PAID,
        transactionID = charge.id,
        method = models.Payment.METHOD_STRIPE,
        invoice = invoice
      )
      messages.info(request, "Your payment has been processed. Thanks!")
      return HttpResponseRedirect(reverse('home'))
    except stripe.CardError, e:
      messages.error(request, "There was an error while processing your card: %s"%(e.message))
  return render_to_response('payment/pay.html',
      {'form': form, 'invoice': invoice},
      context_instance=RequestContext(request))
