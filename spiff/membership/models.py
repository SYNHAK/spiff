from django.db import models
from django.template import RequestContext
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from openid_provider.models import OpenID
from spiff.membership.utils import monthRange
from django.contrib.sites.models import get_current_site
import datetime
import stripe
from django.conf import settings
from spiff.payment.models import LineItem, Invoice
from django.template.loader import get_template
from django.template import Context

stripe.api_key = settings.STRIPE_KEY

if not hasattr(settings, 'ANONYMOUS_USER_ID'):
  settings.ANONYMOUS_USER_ID = 0

class Member(models.Model):
  tagline = models.CharField(max_length=255)
  user = models.OneToOneField(User, related_name='member')
  created = models.DateTimeField(editable=False, auto_now_add=True)
  lastSeen = models.DateTimeField(editable=False, auto_now_add=True)
  fields = models.ManyToManyField('Field', through='FieldValue')
  stripeID = models.TextField()
  hidden = models.BooleanField(default=False)

  def isAnonymous(self):
    return self.user_id == get_anonymous_user().id

  class Meta:
    permissions = (
      ('can_view_hidden_members', 'Can view hidden members'),
      ('list_members', 'Can list members'),
    )

  def generateMonthlyInvoice(self):
    if not self.billedForMonth():
      if self.highestRank is not None and self.highestRank.monthlyDues > 0:
        startOfMonth, endOfMonth = monthRange()
        invoice = Invoice.objects.create(
          user=self.user,
          dueDate=endOfMonth,
        )
        for group in self.user.groups.all():
          if group.rank.monthlyDues > 0:
            lineItem = RankLineItem.objects.create(
              rank = group.rank,
              member = self,
              activeFromDate=startOfMonth,
              activeToDate=endOfMonth,
              invoice=invoice
            )
        invoice.draft = False
        invoice.open = True
        invoice.save()
        return invoice
    return None

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

  def billedForMonth(self, date=None):
    return len(self.getMembershipLineItemsForMonth(date)) > 0

  @property
  def membershipExpiration(self):
    items = self.getMembershipLineItemsForMonth()
    if len(items) > 0:
      return items[0].activeToDate
    return None

  def getMembershipLineItemsForMonth(self, date=None):
    monthStart, monthEnd = monthRange(date)
    billedMonths = self.rankLineItems.filter(
      activeFromDate__gte=monthStart,
      activeToDate__lte=monthEnd
    )
    return billedMonths

  def paidForMonth(self, date=None):
    billedMonths = self.getMembershipLineItemsForMonth(date)
    if len(billedMonths) == 0:
      return False
    for lineItem in billedMonths:
      if billedMonths.invoice.unpaidBalance() > 0:
        return False
    return True

  def activeMember(self):
    if not self.user.is_active:
      return False
    groups = self.user.groups.filter(rank__isActiveMembership=True)
    return len(groups) > 0

  def __unicode__(self):
    if self.hidden:
      return "Anonymous"
    return "%s, %s"%(self.user.last_name, self.user.first_name)

class Rank(models.Model):
  description = models.TextField(blank=True)
  monthlyDues = models.FloatField(default=0)
  group = models.OneToOneField(Group)
  isActiveMembership = models.BooleanField(default=False)
  isKeyholder = models.BooleanField(default=False)

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
            self.name = "%s membership dues for %s, %s to %s"%(self.rank, self.member, self.activeFromDate, self.activeToDate)
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

class AnonymousUser(User):
  def is_anonymous(self):
    return True

  class Meta:
    proxy = True

def get_anonymous_user():
  if settings.ANONYMOUS_USER_ID == 0:
    try:
      user = AnonymousUser.objects.get(
        username='anonymous'
      )
    except AnonymousUser.DoesNotExist:
      user = AnonymousUser.objects.create(
        username='anonymous',
        email='anonymous@example.com',
        password='',
        first_name='Guest',
        last_name='McGuesterson',
      )
      user.set_unusable_password()
      user.save()
      member = Member.objects.get(user=user)
      member.hidden = True
      member.save()
  else:
    user = User.objects.get(settings.ANONYMOUS_USER_ID)
  try:
    member = user.member
  except Member.DoesNotExist:
    user.member, created = Member.objects.get_or_create(user=user)
    user.save()
  return user

post_save.connect(create_member, sender=AnonymousUser)
