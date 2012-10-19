from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save

class Member(models.Model):
  firstName = models.CharField(max_length=100, null=False)
  lastName = models.CharField(max_length=100, null=False)
  tagline = models.CharField(max_length=255)
  profession = models.CharField(max_length=255)
  user = models.OneToOneField(User)
  created = models.DateTimeField(editable=False, auto_now_add=True)
  lastSeen = models.DateTimeField(editable=False, auto_now_add=True)

  @property
  def fullName(self):
    return "%s %s"%(self.firstName, self.lastName)

  def __unicode__(self):
    return "%s, %s"%(self.lastName, self.firstName)

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

def create_member(sender, instance, created, **kwargs):
  if created:
    Member.objects.get_or_create(user=instance)

post_save.connect(create_member, sender=User)

def create_rank(sender, instance, created, **kwargs):
  if created:
    Rank.objects.get_or_create(group=instance)

post_save.connect(create_rank, sender=Group)
