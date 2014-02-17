from django.core.management import BaseCommand
from spiff.events.models import Event
from optparse import make_option
import datetime

class Command(BaseCommand):
  help = 'Generates summaries of upcoming events, suitable for mailing lists'
  option_list = BaseCommand.option_list + (
    make_option('--today',
      action='store_true',
      dest='today',
      default=False,
      help='Show today\'s events'
    ),
    make_option('--delta',
      dest='delta',
      default=7,
      help='Show events within the next X days'
    )
  )

  def handle(self, *args, **options):
    if options['today']:
      now = datetime.date.today()
      cutoff = datetime.datetime(now.year, now.month, now.day, 23, 59, 59)
    else:
      delta = datetime.timedelta(days=options['delta'])
      cutoff = datetime.date.today() + delta
    events = Event.objects.filter(end__lt=cutoff)
    for event in events:
      print "= %s ="%(event.name)
      print "Start: %s"%(event.start)
      print "End: %s"%(event.end)
      orgs = [str(event.creator)]
      for organizer in event.organizers.all():
        orgs.append(str(organizer))
      print "Organizers: %s"%(', '.join(orgs))
      print "\n", event.description, "\n\n"
