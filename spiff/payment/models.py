from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import utc
import datetime
import stripe
from spiff import funcLog

from spiff.notification_loader import notification
notification = None
from spiff.api.plugins import find_api_classes

class InvoiceManager(models.Manager):

    def allOpen(self):
        return self.filter(open=True, draft=False)

    def unpaid(self):
        ids = []
        for i in self.allOpen():
            if i.unpaidBalance > 0:
                ids.append(i.id)
        return self.filter(id__in=ids, draft=False)

    def pastDue(self):
        return self.unpaid().filter(dueDate__lt=datetime.date.utcnow().replace(tzinfo=utc), draft=False)

class Invoice(models.Model):
    user = models.ForeignKey(User, related_name='invoices')
    created = models.DateTimeField(auto_now_add=True)
    dueDate = models.DateField()
    open = models.BooleanField(default=True)
    draft = models.BooleanField(default=True)

    @classmethod
    def bundleLineItems(cls, user, dueDate, items):
      if len(items) == 0:
        return None

      invoice = Invoice.objects.create(
        user = user,
        dueDate = dueDate,
      )
      for item in items:
        item.invoice = invoice
        item.save()
      return invoice

    class Meta:
      permissions = (
        ('view_other_invoices', 'Can view invoices assigned to other users'),
      )

    def chargeStripe(self):
      stripeCustomer = self.user.member.stripeCustomer()
      charge = stripe.Charge.create(
        amount = int(self.unpaidBalance*100),
        currency = 'usd',
        description = 'Payment from %s for invoice %s'%(self.user.member.fullName, self.id),
        customer = stripeCustomer.id
      )
      Payment.objects.create(
        user = self.user,
        value = self.unpaidBalance,
        status = Payment.STATUS_PAID,
        transactionID = charge.id,
        method = Payment.METHOD_STRIPE,
        invoice = self
      )

    def save(self, *args, **kwargs):
      if self.pk and notification:
        current = Invoice.objects.get(pk=self.pk)
        if current.draft == True or current.open == False:
          if self.draft == False and self.open == True and self.unpaidBalance > 0:
            try:
              self.chargeStripe()
            except stripe.error.CardError, e:
              funcLog().error("Failed to charge stripe")
              funcLog().exception(e)
              notification.send(
                [self.user],
                "card_failed",
                {'user': self.user, 'invoice': self})
      super(Invoice, self).save(*args, **kwargs)

    @property
    def unpaidBalance(self):
        return self.total - self.paidBalance

    @property
    def paidBalance(self):
        sum = 0
        for p in self.payments.all():
            sum += p.value
        return sum

    objects = InvoiceManager()

    @property
    def total(self):
        sum = 0
        for s in self.items.all():
            sum += s.totalPrice
        for d in self.discounts.all():
            sum -= d.value
        return sum

    def __unicode__(self):
        return "Invoice %d"%(self.id)

    @property
    def isOverdue(self):
      return self.dueDate < datetime.date.utcnow().replace(tzinfo=utc) and self.draft is False 

class LineItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items')
    name = models.TextField()
    unitPrice = models.FloatField(default=0)
    quantity = models.FloatField(default=1)

    def isOpen(self):
        return self.invoice.open

    def process(self):
      pass

    @property
    def totalPrice(self):
        return self.unitPrice * self.quantity

    def __unicode__(self):
        return "%d %s @%d ea, %s"%(self.quantity, self.name, self.unitPrice, self.invoice)

class LineDiscountItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='discounts')
    description = models.TextField()
    flatRate = models.FloatField(default=0)
    percent = models.FloatField(default=0)
    lineItem = models.ForeignKey(LineItem, related_name='discounts')

    @property
    def value(self):
      """Returns the positive value to subtract from the total."""
      originalPrice = self.lineItem.totalPrice
      if self.flatRate == 0:
        return originalPrice * self.percent
      return self.flatRate

class CreditManager(models.Manager):
    def forUser(self, user):
        return self.filter(user=user)

    def userTotal(self, user):
        totalCredit = self.forUser(user).aggregate(models.Sum('value'))
        totalUsedCredit = Payment.objects.filter(user=user,
            method=Payment.METHOD_CREDIT).aggregate(models.Sum('value'))
        if totalUsedCredit['value__sum'] is None:
          totalUsedCredit['value__sum'] = 0
        if totalCredit['value__sum'] is None:
          totalCredit['value__sum'] = 0
        return totalCredit['value__sum'] - totalUsedCredit['value__sum']

class Credit(models.Model):
    objects = CreditManager()

    user = models.ForeignKey(User, related_name='credits')
    value = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

class Payment(models.Model):
    METHOD_CASH = 0
    METHOD_CHECK = 1
    METHOD_STRIPE = 2
    METHOD_OTHER = 3
    METHOD_CREDIT = 4
    METHODS = (
        (METHOD_CASH, 'Cash'),
        (METHOD_CHECK, 'Check'),
        (METHOD_STRIPE, 'Stripe'),
        (METHOD_OTHER, 'Other'),
        (METHOD_CREDIT, 'Credit'),
    )
    STATUS_PENDING = 0
    STATUS_PAID = 1
    STATUS = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_PAID, 'Paid'),
    )
    user = models.ForeignKey(User, related_name='payments')
    value = models.FloatField()
    created = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=STATUS_PENDING, choices=STATUS)
    transactionID = models.TextField(blank=True, null=True)
    method = models.IntegerField(choices=METHODS)
    invoice = models.ForeignKey(Invoice, related_name='payments')

    def save(self, *args, **kwargs):
        if not self.id and not self.created:
            self.created = datetime.datetime.utcnow().replace(tzinfo=utc)
            if notification:
              notification.send(
                [self.user],
                "payment_received",
                {'user': self.user, 'payment': self})
        super(Payment, self).save(*args, **kwargs)
        if self.invoice.unpaidBalance == 0:
            self.invoice.open = False
            self.invoice.save()
            for lineItemType in find_api_classes('models', LineItem):
              for item in lineItemType.objects.filter(invoice=self.invoice):
                item.process()

    def __unicode__(self):
        return "%d %s by %s for %s"%(self.value, self.get_method_display(), self.user, self.invoice)

