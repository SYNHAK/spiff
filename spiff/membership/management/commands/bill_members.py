from django.core.management import BaseCommand
from spiff.membership.utils import monthRange
from spiff.membership.models import Member, RankLineItem
from spiff.payment.models import Invoice

class Command(BaseCommand):
  help = 'Bills active members for the month'

  def handle(self, *args, **options):
    for member in Member.objects.all():
      if not member.billedForMonth():
        if member.highestRank is not None and member.highestRank.monthlyDues > 0:
          print "Billing", member, "for the month"
          endOfMonth, startOfMonth = monthRange()
          invoice = Invoice.objects.create(
            user=member.user,
            dueDate=endOfMonth,
          )
          for group in member.user.groups.all():
            if group.rank.monthlyDues > 0:
              lineItem = RankLineItem.objects.create(
                rank = group.rank,
                member = member,
                activeFromDate=startOfMonth,
                activeToDate=endOfMonth,
                invoice=invoice
              )
              print "\tCreated", lineItem
          invoice.draft = False
          invoice.save()
          print "\tInvoice saved!"
      else:
        print "%s has outstanding balance of $%s"%(
          member,
          member.outstandingBalance
        )
