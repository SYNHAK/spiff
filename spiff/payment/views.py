from django.template import RequestContext
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.conf import settings
import stripe
from django.http import HttpResponseRedirect
from django.contrib import messages
import models
import forms
from django.shortcuts import render_to_response
from spiff.notification_loader import notification

def viewInvoice(request, invoiceID):
  invoice = models.Invoice.objects.get(pk=invoiceID)
  if not (request.user.has_perm('payment.view_other_invoices') or invoice.user != request.user):
    raise PermissionDenied()
  return render_to_response('payment/viewInvoice.html',
    {'invoice': invoice},
    context_instance=RequestContext(request))

def addPayment(request, invoiceID):
  invoice = models.Invoice.objects.get(pk=invoiceID)
  if request.method == 'POST':
    form = forms.AddPaymentForm(request.POST)
  else:
    form = forms.AddPaymentForm()
  if form.is_valid():
    payment = models.Payment.objects.create(
      user = form.cleaned_data['user'],
      value = form.cleaned_data['value'],
      created = form.cleaned_data['created'],
      method = form.cleaned_data['method'],
      invoice = invoice
    )
    if notification:
      notification.send(
        [payment.user],
        'payment_received',
        {'user': invoice.user, 'payment': payment}
      )
      messages.info(request, "Payment added.")
    return HttpResponseRedirect(reverse('payment:viewInvoice', kwargs={'invoiceID': invoice.id}))
  return render_to_response('payment/addPayment.html',
    {'invoice': invoice, 'form': form},
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
      if notification:
        notification.send(
          [request.user],
          'payment_received',
          {'user': request.user, 'payment': payment}
        )
      messages.info(request, "Your payment has been processed. Thanks!")
      return HttpResponseRedirect(reverse('home'))
    except stripe.CardError, e:
      messages.error(request, "There was an error while processing your card: %s"%(e.message))
  return render_to_response('payment/pay.html',
      {'form': form, 'invoice': invoice},
      context_instance=RequestContext(request))
