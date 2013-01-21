from django.core.management import BaseCommand
from django.contrib.auth.models import Permission

class Command(BaseCommand):
  help = 'Outputs all available permissions implemented in Spiff'

  def handle(self, *args, **options):
    ret = []
    for p in Permission.objects.all():
        ret.append("%s.%s: %s"%(p.content_type.app_label, p.codename, p.name))
    for r in sorted(ret):
        print r
