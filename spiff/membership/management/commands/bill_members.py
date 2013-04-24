from django.core.management import BaseCommand
from spiff.membership.utils import monthRange
from spiff.membership.models import Member, RankLineItem
from spiff.payment.models import Invoice

class Command(BaseCommand):
  help = 'Bills active members for the month'

  def handle(self, *args, **options):
    for member in Member.objects.all():
      invoice = member.generateMonthlyInvoice()
      if invoice:
        print "Billed", member, "for the month:"
        for item in invoice.items.all():
          print "\t", item
      else:
        print "%s has outstanding balance of $%s"%(
          member,
          member.outstandingBalance
        )
