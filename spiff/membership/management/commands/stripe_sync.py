from django.core.management import BaseCommand
from spiff.membership.models import Member
from django.conf import settings
import stripe

class Command(BaseCommand):
  help = 'Updates Customers and Plans in Stripe'

  def handle(self, *args, **options):
    stripe.api_key = settings.STRIPE_KEY
    members = Member.objects.all()
    validCustomers = []
    for member in members:
      customer = None
      plan = None
      if member.highestRank is not None:
        plan = member.highestRank.id
      try:
        customer = stripe.Customer.retrieve(member.stripeID)
        if customer.active_card is not None or plan is None:
          customer.plan = plan
          customer.save()
        print "Synced", member, 'with', customer.id
      except stripe.InvalidRequestError:
        customer = stripe.Customer.create(
          description=member.fullName,
          email=member.user.email
        )
        member.stripeID = customer.id
        member.save()
        print "Created new customer for", member
      validCustomers.append(customer.id)
    count = 100
    offset = 0
    while True:
      customers = stripe.Customer.all(count=count, offset=offset)
      for c in customers['data']:
        if c.id in validCustomers:
          continue
        else:
          print "Cleaning up old customer", c.description, c.id
          c.delete()
      if len(customers['data']) < count:
        break
