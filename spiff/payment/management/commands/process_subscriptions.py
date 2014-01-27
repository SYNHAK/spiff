from django.core.management import BaseCommand
from spiff.payment.models import SubscriptionPlan, Invoice
from spiff.api import find_api_classes
from spiff.membership.utils import monthRange
from spiff.membership.models import Member, RankLineItem

class Command(BaseCommand):
  help = 'Bills active members for the month'

  def handle(self, *args, **options):
    startOfMonth, endOfMonth = monthRange()
    lineItems = {}
    for planCls in find_api_classes('models', SubscriptionPlan):
      plans = planCls.objects.all()
      for plan in plans:
        for subscription in plan.subscriptions.filter(active=True):
          if subscription.user not in lineItems:
            lineItems[subscription.user] = {'subscriptions': [], 'lineItems': []}

          items = plan.process(subscription)

          if len(items) > 0 and subscription not in lineItems[subscription.user]['subscriptions']:
            lineItems[subscription.user]['subscriptions'].append(subscription)
            lineItems[subscription.user]['lineItems'] += items
    for user, data in lineItems.iteritems():
      invoice = Invoice.bundleLineItems(user, endOfMonth, data['lineItems'])
      if invoice:
        print "Created invoice", invoice
      for subscription in data['subscriptions']:
        subscription.save()
