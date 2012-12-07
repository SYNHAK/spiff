from django.core.management import BaseCommand
from spiff.membership.models import Rank, Member
from django.conf import settings
import stripe

class Command(BaseCommand):
  help = 'Updates Customers and Plans in Stripe'

  def handle(self, *args, **options):
    stripe.api_key = settings.STRIPE_KEY
    ranks = Rank.objects.filter(monthlyDues__gt=0)
    plans = stripe.Plan.all()['data']
    deletedPlans = []
    for plan in plans:
      isGone = True
      for rank in ranks:
        if str(rank.id) == str(plan.id):
          isGone = False
          break
      if isGone:
        print "Removing plan %s"%(plan.name)
        plan.delete()
    for rank in ranks:
      exists = False
      for plan in plans:
        if str(rank.id) == str(plan.id):
          if plan.amount != int(rank.monthlyDues*100):
            print "Plan", plan.name, "does not match rank", rank, ", deleting."
            plan.delete()
          else:
            exists = True
            if plan.name != rank.group.name:
              print "Syncing plan", plan.name, 'with rank', rank
              plan.name = rank.group.name
              plan.save()
            break
      if not exists:
        print "Creating plan for", rank
        plan = stripe.Plan.create(
          amount = int(rank.monthlyDues*100),
          interval = 'month',
          name = rank.group.name,
          currency = 'usd',
          id = rank.id
        )
    members = Member.objects.all()
    validCustomers = []
    for member in members:
      isGone = True
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
