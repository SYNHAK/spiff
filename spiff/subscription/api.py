from django.db import transaction
from spiff.api.plugins import find_api_classes
from spiff.subscription.models import SubscriptionPlan
from spiff.payment.models import Invoice
from spiff.membership.utils import monthRange
from spiff import funcLog

def processSubscriptions():
  with transaction.atomic():
    startOfMonth, endOfMonth = monthRange()
    lineItems = {}
    for planCls in find_api_classes('models', SubscriptionPlan):
      plans = planCls.objects.all()
      for plan in plans:
        for subscription in plan.subscriptions.filter(active=True):
          if subscription.user not in lineItems:
            lineItems[subscription.user] = {'subscriptions': [], 'lineItems': []}

          items = plan.process(subscription)
          funcLog().info("Processed subscription %s", subscription)

          if len(items) > 0 and subscription not in lineItems[subscription.user]['subscriptions']:
            lineItems[subscription.user]['subscriptions'].append(subscription)
            lineItems[subscription.user]['lineItems'] += items
    invoices = []
    for user, data in lineItems.iteritems():
      invoice = Invoice.bundleLineItems(user, endOfMonth, data['lineItems'])
      if invoice:
        funcLog().info("Created invoice %s", invoice)
        invoices.append(invoice)
      for subscription in data['subscriptions']:
        subscription.save()
    for invoice in invoices:
      invoice.draft = False
      invoice.save()
