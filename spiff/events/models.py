from django.db import models
from django.contrib.auth.models import User
from spiff.membership.models import Member
from spiff.inventory.models import Resource

class Event(models.Model):
  """Represents an event at the space.

  Events can have:
  * start
  * end
  * name
  * description
  * list of organizers
  * list of attendees
  * list of attached resources

  """
  start = models.DateTimeField()
  end = models.DateTimeField()
  name = models.TextField()
  description = models.TextField()
  attendees = models.ManyToManyField(Member, related_name='events')
  creator = models.ForeignKey(Member, related_name='owned_events')
  organizers = models.ManyToManyField(User, related_name='organized_events')
  resources = models.ManyToManyField(Resource, related_name='events', blank=True)

  class Meta:
    permissions = (
      ('can_reserve_resource', 'Can attach resources to events'),
    )

  @models.permalink
  def get_absolute_url(self):
    return ('events:view', [], {'id': self.id})

  def __unicode__(self):
    return self.name
