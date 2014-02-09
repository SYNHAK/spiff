from django.core.management import BaseCommand
from spiff.payment.models import Invoice
import stripe

class Command(BaseCommand):
  help = 'Attempts to process an invoice via stripe'

  def handle(self, *args, **options):
    for invoice in Invoice.objects.unpaid().all():
      print invoice
      try:
        unpaid = invoice.unpaidBalance
        invoice.chargeStripe()
        print "Paid %s"%(unpaid)
      except stripe.error.CardError, e:
        print "Could not process card.", e
