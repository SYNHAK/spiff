from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
import datetime

class Member(models.Model):
  tagline = models.CharField(max_length=255)
  profession = models.CharField(max_length=255)
  user = models.OneToOneField(User)
  created = models.DateTimeField(editable=False, auto_now_add=True)
  lastSeen = models.DateTimeField(editable=False, auto_now_add=True)
  fields = models.ManyToManyField('Field', through='FieldValue')
  birthday = models.DateField(blank=True, null=True)

  @models.permalink
  def get_absolute_url(self):
    return ('spiff.membership.views.view', [], {'username': self.user.username})

  @property
  def fullName(self):
    return "%s %s"%(self.user.first_name, self.user.last_name)

  def paidForMonth(self):
    now = datetime.date.today()
    firstOfMonth = datetime.date(now.year, now.month, 1)
    payments = self.payments.filter(created__gt=firstOfMonth)
    return len(payments) > 0

  def overdue(self):
    now = datetime.date.today()
    firstOfMonth = datetime.date(now.year, now.month, 1)
    lateDate = firstOfMonth+datetime.timedelta(days=30)
    payments = self.payments.filter(created__lt=lateDate)
    return len(payments) == 0

  def __unicode__(self):
    return "%s, %s"%(self.user.last_name, self.user.first_name)

class DuePayment(models.Model):
  member = models.ForeignKey(Member, related_name='payments')
  value = models.FloatField()
  created = models.DateTimeField(editable=True)
  rank = models.ForeignKey('Rank', related_name='payments')

  def __unicode__(self):
    return "%s from %s"%(self.value, self.member.fullName)

class Rank(models.Model):
  description = models.TextField(blank=True)
  monthlyDues = models.FloatField(default=0)
  group = models.OneToOneField(Group)

  def __unicode__(self):
    return self.group.name

class Field(models.Model):
  name = models.CharField(max_length=100)
  description = models.TextField(blank=True)
  required = models.BooleanField(default=False)
  public = models.BooleanField(default=False)
  protected = models.BooleanField(default=False)

  class Meta:
    permissions = (
      ('can_view_private_fields', 'Can view private fields'),
      ('can_edit_protected_fields', 'Can edit protected fields'),
    )

  def __unicode__(self):
    return self.name

class FieldValue(models.Model):
  field = models.ForeignKey(Field)
  member = models.ForeignKey(Member, related_name='attributes')
  value = models.TextField()

  def __unicode__(self):
    return "%s: %s = %s"%(self.member.fullName, self.field.name, self.value)

def create_member(sender, instance, created, **kwargs):
  if created:
    Member.objects.get_or_create(user=instance)

post_save.connect(create_member, sender=User)

def create_rank(sender, instance, created, **kwargs):
  if created:
    Rank.objects.get_or_create(group=instance)

post_save.connect(create_rank, sender=Group)
