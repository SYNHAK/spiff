from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import utc
import datetime

from spiff.notification_loader import notification

class InvoiceManager(models.Manager):

    def allOpen(self):
        return self.filter(open=True, draft=False)

    def unpaid(self):
        ids = []
        for i in self.filter(open=True):
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

    class Meta:
      permissions = (
        ('view_other_invoices', 'Can view invoices assigned to other users'),
      )

    def save(self, *args, **kwargs):
      if self.pk and notification:
        current = Invoice.objects.get(pk=self.pk)
        if current.draft == True or current.open == False:
          if self.draft == False and self.open == True and self.unpaidBalance > 0:
            notification.send(
              [self.user],
              "invoice_ready",
              {'user': self.user, 'invoice': self},
            ) 
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

    @models.permalink
    def get_absolute_url(self):
      return ("payment:viewInvoice", [], {"invoiceID": self.id})

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

    @property
    def totalPrice(self):
        return self.unitPrice * self.quantity

    def __unicode__(self):
        return "%d %s @%d ea, %s"%(self.unitPrice, self.name, self.quantity, self.invoice)

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
    created = models.DateTimeField()
    status = models.IntegerField(default=STATUS_PENDING, choices=STATUS)
    transactionID = models.TextField(blank=True, null=True)
    method = models.IntegerField(choices=METHODS)
    invoice = models.ForeignKey(Invoice, related_name='payments')

    def save(self, *args, **kwargs):
        if not self.id and not self.created:
            self.created = datetime.datetime.utcnow().replace(tzinfo=utc)
        super(Payment, self).save(*args, **kwargs)
        if self.invoice.unpaidBalance == 0:
            self.invoice.open = False
            self.invoice.save()

    def __unicode__(self):
        return "%d %s by %s for %s"%(self.value, self.get_method_display(), self.user, self.invoice)
