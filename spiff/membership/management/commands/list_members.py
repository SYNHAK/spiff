from django.core.management import BaseCommand
from spiff.membership.models import Member

class Command(BaseCommand):
  help = 'Lists active member email addresses'

  def handle(self, *args, **options):
    members = Member.objects.all()
    for m in members:
      if m.activeMember():
        print m.user.email
