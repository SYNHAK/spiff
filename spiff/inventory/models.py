from django.db import models
from spiff.membership.models import Member

class Resource(models.Model):
  name = models.TextField()
  trainable = models.BooleanField(default=True)
  users = models.ManyToManyField(Member, through='TrainingLevel',
      limit_choices_to={'is_active': True})

  @models.permalink
  def get_absolute_url(self):
    return ('spiff.inventory.views.view', [], {'id':self.id})
  
  def __unicode__(self):
    return self.name

META_TYPES = (
  (0, 'string'),
  (1, 'url'),
  (2, 'image'),
)

class Metadata(models.Model):
  name = models.TextField()
  type = models.IntegerField(choices=META_TYPES)
  value = models.TextField()
  resource = models.ForeignKey(Resource, related_name='metadata')

  def __unicode__(self):
    return self.value

class TrainingLevel(models.Model):
  member = models.ForeignKey(Member, related_name='trainings')
  resource = models.ForeignKey(Resource, related_name='trainings')
  rank = models.IntegerField()
  comments = models.TextField(blank=True)

  def __unicode__(self):
    return "%s: level %d %s user"%(self.member.fullName, self.rank, self.resource.name)
