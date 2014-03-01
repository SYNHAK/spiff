from django.core.management import BaseCommand
from spiff.subscription.api import processSubscriptions

class Command(BaseCommand):
  help = 'Bills active members for the month'

  def handle(self, *args, **options):
    processSubscriptions()
