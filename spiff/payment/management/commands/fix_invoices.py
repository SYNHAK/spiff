from django.core.management import BaseCommand
from spiff.payment.models import Invoice

class Command(BaseCommand):
    help = 'Closes invoices that are paid but still open'

    def handle(self, *args, **options):
        invoices = Invoice.objects.all()
        for i in invoices:
            if i.unpaidBalance == 0 and not i.open:
                i.open = False
                i.save()
                print "Closed", i
