from django.db import models
from spiff.membership.models import Member

class Resource(models.Model):
  name = models.TextField()
  trainable = models.BooleanField(default=True)
  users = models.ManyToManyField(Member, through='TrainingLevel',
      limit_choices_to={'is_active': True})
  certified_users = models.ManyToManyField(Member, through='Certification', related_name='certified_resources')

  def __unicode__(self):
    return self.name

  def logChange(self, member, trained_member=None, property=None, old=None, new=None):
    Change.objects.create(
        resource=self,
        member=member,
        old=old,
        new=new,
        property=property,
        trained_member=trained_member)

#: Available metadata types, given as hints to clients.
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

  class Meta:
    permissions = (
      ('can_train', 'Can update own training on resources'),
      ('certify', 'Can certify other users'),
    )
    ordering = ['-rank']

  def __unicode__(self):
    return "%s: level %d %s user"%(self.member.fullName, self.rank, self.resource.name)

class Certification(models.Model):
  member = models.ForeignKey(Member, related_name='certifications')
  resource = models.ForeignKey(Resource, related_name='certifications')
  comment = models.TextField()

  def __unicode__(self):
    return "%s: Certified on %s: %s"%(self.member.fullName, self.comment, self.resource.name)

class Change(models.Model):
  resource = models.ForeignKey(Resource, related_name='changelog')
  member = models.ForeignKey(Member, related_name='changes')
  trained_member = models.ForeignKey(Member, related_name='training_changes',
      null=True, blank=True)
  old = models.TextField(null=True, blank=True)
  new = models.TextField(null=True, blank=True)
  property = models.TextField(null=True, blank=True)
  stamp = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-stamp']

  def __unicode__(self):
    if self.trained_member:
      name = "%s's training on %s"%(self.trained_member, self.resource)
    if self.property:
      name = "%s:%s"%(self.resource, self.property)
    return "%s: %s -> %s"%(name, self.old, self.new)
