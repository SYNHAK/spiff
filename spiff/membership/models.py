from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from openid_provider.models import OpenID
import datetime
import stripe
from django.conf import settings
from spiff.payment.models import LineItem, Invoice

stripe.api_key = settings.STRIPE_KEY

class Member(models.Model):
  tagline = models.CharField(max_length=255)
  profession = models.CharField(max_length=255)
  user = models.OneToOneField(User)
  created = models.DateTimeField(editable=False, auto_now_add=True)
  lastSeen = models.DateTimeField(editable=False, auto_now_add=True)
  fields = models.ManyToManyField('Field', through='FieldValue')
  birthday = models.DateField(blank=True, null=True)
  stripeID = models.TextField()
  hidden = models.BooleanField(default=False)

  class Meta:
    permissions = (
      ('can_view_hidden_members', 'Can view hidden members'),
    )

  def stripeCustomer(self):
    try:
      customer = stripe.Customer.retrieve(self.stripeID)
    except stripe.InvalidRequestError:
      customer = stripe.Customer.create(
        description = self.fullName,
        email = self.user.email
      )
      self.stripeID = customer.id
      self.save()
    return customer

  def serialize(self):
    return {
      'profession': self.profession,
      'firstName': self.user.first_name,
      'lastName': self.user.last_name,
      'created': self.created,
      'lastSeen': self.lastSeen,
      'email': self.user.email,
      'fields': self.fields.filter(public=True),
      'id': self.id,
      'active': self.activeMember(),
    }

  @property
  def highestRank(self):
    groups = self.user.groups.extra(order_by=['-rank__monthlyDues'])
    if len(groups) > 0:
      return groups[0].rank
    return None

  @models.permalink
  def get_absolute_url(self):
    return ('membership:view', [], {'user__username': self.user.username})

  @property
  def fullName(self):
    if self.hidden:
      return "Anonymous"
    else:
      return "%s %s"%(self.user.first_name, self.user.last_name)

  @property
  def outstandingBalance(self):
    sum = 0
    invoices = self.user.invoices.unpaid()
    for i in invoices:
        sum += i.unpaidBalance
    return sum

  @property
  def overdue(self):
    return len(self.user.invoices.pastDue()) > 0

  @property
  def keyholder(self):
    groups = self.user.groups.filter(rank__isKeyholder=True)
    return len(groups) > 0

  def activeMember(self):
    if not self.user.is_active:
      return False
    groups = self.user.groups.filter(rank__isActiveMembership=True)
    return len(groups) > 0

  def __unicode__(self):
    if self.hidden:
      return "Anonymous"
    return "%s, %s"%(self.user.last_name, self.user.first_name)

class DuePayment(models.Model):
  METHOD_CASH = 0
  METHOD_CHECK = 1
  METHOD_STRIPE = 2
  METHOD_OTHER = 3
  METHODS = (
    (METHOD_CASH, 'Cash'),
    (METHOD_CHECK, 'Check'),
    (METHOD_STRIPE, 'Stripe'),
    (METHOD_OTHER, 'Other'),
  )
  STATUS_PENDING = 0
  STATUS_PAID = 1
  STATUS = (
    (STATUS_PENDING, 'Pending'),
    (STATUS_PAID, 'Paid'),
  )
  member = models.ForeignKey(Member, related_name='payments')
  user = models.ForeignKey(User)
  value = models.FloatField()
  created = models.DateTimeField()
  rank = models.ForeignKey('Rank', related_name='payments')
  status = models.IntegerField(default=STATUS_PENDING, choices=STATUS)
  transactionID = models.TextField(blank=True, null=True)
  method = models.IntegerField(choices=METHODS)

  def save(self, *args, **kwargs):
    if not self.id and not self.created:
      self.created = datetime.datetime.today()
    super(DuePayment, self).save(*args, **kwargs)

  def __unicode__(self):
    return "%s from %s"%(self.value, self.member.fullName)

class Rank(models.Model):
  description = models.TextField(blank=True)
  monthlyDues = models.FloatField(default=0)
  group = models.OneToOneField(Group)
  isActiveMembership = models.BooleanField()
  isKeyholder = models.BooleanField()

  class Meta:
    permissions = (
      ('can_change_member_rank', 'Can change member ranks'),
      ('can_view_member_rank', 'Can view member ranks'),
      ('can_deactivate_user', 'Can deactivate a user account'),
    )

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

class RankLineItem(LineItem):
    rank = models.ForeignKey(Rank)
    member = models.ForeignKey(Member, related_name='rankLineItems')
    activeFromDate = models.DateTimeField(default=datetime.datetime.utcnow())
    activeToDate = models.DateTimeField(default=datetime.datetime.utcnow())

    def save(self, *args, **kwargs):
        if not self.id:
            if self.unitPrice == 0:
              self.unitPrice = self.rank.monthlyDues
            self.name = "%s membership dues"%(self.rank)
        super(RankLineItem, self).save(*args, **kwargs)

def create_member(sender, instance, created, **kwargs):
  if created:
    Member.objects.get_or_create(user=instance)
    OpenID.objects.get_or_create(user=instance, default=True)

post_save.connect(create_member, sender=User)

def create_rank(sender, instance, created, **kwargs):
  if created:
    Rank.objects.get_or_create(group=instance)

post_save.connect(create_rank, sender=Group)
