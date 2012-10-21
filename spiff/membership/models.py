from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save

class Member(models.Model):
  tagline = models.CharField(max_length=255)
  profession = models.CharField(max_length=255)
  user = models.OneToOneField(User)
  created = models.DateTimeField(editable=False, auto_now_add=True)
  lastSeen = models.DateTimeField(editable=False, auto_now_add=True)
  fields = models.ManyToManyField('Field', through='FieldValue')
  birthday = models.DateField(blank=True, null=True)

  @property
  def fullName(self):
    return "%s %s"%(self.user.first_name, self.user.last_name)

  def __unicode__(self):
    return "%s, %s"%(self.user.last_name, self.user.first_name)

class DuePayment(models.Model):
  member = models.ForeignKey(Member, related_name='payments')
  value = models.FloatField()
  created = models.DateTimeField(auto_now_add=True)

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
  multiple = models.BooleanField(default=False)
  required = models.BooleanField(default=False)

  def __unicode__(self):
    return self.name

class FieldValue(models.Model):
  field = models.ForeignKey(Field)
  member = models.ForeignKey(Member)
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
