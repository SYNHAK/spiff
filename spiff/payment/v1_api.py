from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.exceptions import ImmediateHttpResponse
from spiff.notification_loader import notification
import stripe
import models
from django.conf import settings
from tastypie import fields

class PaymentResource(ModelResource):
  invoice = fields.ToOneField('spiff.api.resources.InvoiceResource', 'invoice')
  value = fields.FloatField('value')

  class Meta:
    queryset = models.Payment.objects.all()
    authorization = Authorization()
    always_return_data = True

  def obj_create(self, bundle, **kwargs):
    bundle = self.full_hydrate(bundle)
    m2m = self.hydrate_m2m(bundle)
    print 'data', bundle.data
    invoice = m2m.obj.invoice
    stripe.api_key = settings.STRIPE_KEY
    cardData = {}
    stripeData = bundle.data['stripe']
    cardData['number'] = stripeData['card']
    cardData['exp_month'] = stripeData['exp_month']
    cardData['exp_year'] = stripeData['exp_year']
    cardData['cvc'] = stripeData['cvc']
    balance = float(bundle.data['value'])
    if balance > invoice.unpaidBalance:
      raise ImmediateHttpResponse(response=self.error_response("You can't pay more than $%s!"%(invoice.unpaidBalance)))
    try:
      charge = stripe.Charge.create(
        amount = int(balance*100),
        currency = 'usd',
        card = cardData,
        description = 'Payment from %s for invoice %s'%(bundle.request.user.member.fullName, invoice.id)
      )
      payment = Payment.objects.create(
        user = bundle.request.user,
        value = balance,
        status = Payment.STATUS_PAID,
        transactionID = charge.id,
        method = Payment.METHOD_STRIPE,
        invoice = invoice
      )
      if notification:
        notification.send(
          [bundle.request.user],
          'payment_received',
          {'user': bundle.request.user, 'payment': payment}
        )
      bundle.obj = payment
    except stripe.CardError, e:
      raise e
    return bundle

class LineItemResource(ModelResource):
  name = fields.CharField(attribute='name')
  unitPrice = fields.FloatField('unitPrice')
  quantity = fields.FloatField('quantity')
  totalPrice = fields.FloatField('totalPrice')

  class Meta:
    querySet = models.LineItem.objects.all()

class InvoiceResource(ModelResource):
  user = fields.ToOneField('spiff.membership.v1_api.MemberResource', 'user__member', null=True, full=True)
  unpaidBalance = fields.FloatField('unpaidBalance')
  paidBalance = fields.FloatField('paidBalance')
  total = fields.FloatField('total')
  items = fields.ToManyField(LineItemResource, 'items', null=True, full=True);
  payments = fields.ToManyField(PaymentResource, 'payments', null=True, full=True);

  class Meta:
    queryset = models.Invoice.objects.all()
