from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from openid_provider.models import OpenID
from spiff.membership.utils import monthRange
import datetime
import stripe
from django.conf import settings
import spiff.payment.models
from spiff.subscription.models import SubscriptionPlan
from spiff import funcLog

stripe.api_key = settings.STRIPE_KEY

if not hasattr(settings, 'ANONYMOUS_USER_ID'):
  settings.ANONYMOUS_USER_ID = 0

if not hasattr(settings, 'AUTHENTICATED_GROUP_ID'):
  settings.AUTHENTICATED_GROUP_ID = 0

class Member(models.Model):
  tagline = models.CharField(max_length=255)
  user = models.OneToOneField(User, related_name='member')
  created = models.DateTimeField(editable=False, auto_now_add=True)
  lastSeen = models.DateTimeField(editable=False, auto_now_add=True)
  fields = models.ManyToManyField('Field', through='FieldValue')
  stripeID = models.TextField()
  hidden = models.BooleanField(default=False)

  @property
  def stripeCards(self):
    customer = self.stripeCustomer()
    if 'cards' in customer:
      return customer.cards.data
    return []

  def addStripeCard(self, cardData):
    customer = self.stripeCustomer()
    return customer.cards.create(
      card = cardData
    )

  def setDefaultStripeCard(self, cardID):
    customer = self.stripeCustomer()
    customer.default_card = cardID
    customer.save()

  def removeStripeCard(self, cardID):
    customer = self.stripeCustomer()
    customer.cards.retrieve(cardID).delete()

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
        invoice = spiff.payment.models.Invoice.objects.create(
          user=self.user,
          dueDate=endOfMonth,
        )
        for group in self.user.groups.all():
          if group.rank.monthlyDues > 0:
            RankLineItem.objects.create(
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
      return self.stripeCustomer()
    if 'deleted' in customer:
      self.stripeID = ""
      self.save()
      return self.stripeCustomer()
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

  def getMembershipLineItemsForMonth(self, rank=None, date=None):
    monthStart, monthEnd = monthRange(date)
    if rank is None:
      billedMonths = self.rankLineItems.filter(
        activeFromDate__gte=monthStart,
        activeToDate__lte=monthEnd,
      )
    else:
      billedMonths = self.rankLineItems.filter(
        activeFromDate__gte=monthStart,
        activeToDate__lte=monthEnd,
        rank=rank,
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

class RankSubscriptionPlan(SubscriptionPlan):
    rank = models.ForeignKey(Rank, related_name='subscriptions')
    member = models.ForeignKey(Member, related_name='rankSubscriptions',
        blank=True, null=True)
    quantity = models.IntegerField(default=1)

    def calculatePeriodCost(self):
      return self.rank.monthlyDues * self.quantity

    def createLineItems(self, subscription, processDate):
      targetMember = self.member
      if targetMember is None:
        targetMember = subscription.user.member
      planOwner = subscription.user
      startOfMonth, endOfMonth = monthRange(processDate)

      funcLog().info("Processing subscription of %s dues for %s, billing to %s", self.rank, self.member, planOwner)

      return [RankLineItem(
        rank = self.rank,
        member = targetMember,
        activeFromDate = startOfMonth,
        activeToDate = endOfMonth
      ),]

    def __unicode__(self):
      return "%sx%s for %s, %s"%(self.rank, self.quantity, self.member, self.period)

class RankLineItem(spiff.payment.models.LineItem):
    rank = models.ForeignKey(Rank)
    member = models.ForeignKey(Member, related_name='rankLineItems')
    activeFromDate = models.DateTimeField(default=datetime.datetime.utcnow())
    activeToDate = models.DateTimeField(default=datetime.datetime.utcnow())

    def process(self):
      period, created = MembershipPeriod.objects.get_or_create(
        rank = self.rank,
        member = self.member,
        activeFromDate = self.activeFromDate,
        activeToDate = self.activeToDate,
        lineItem = self
      )
      if created:
        u = self.member.user
        u.groups.add(self.rank.group)
        u.save()
        funcLog().info("Processed %s - added %s to group %s", self, self.member,
            self.rank.group)

    def save(self, *args, **kwargs):
        if not self.id:
            if self.unitPrice == 0:
              self.unitPrice = self.rank.monthlyDues
            self.name = "%s membership dues for %s, %s to %s"%(self.rank, self.member, self.activeFromDate, self.activeToDate)
        super(RankLineItem, self).save(*args, **kwargs)

class MembershipPeriod(models.Model):
    rank = models.ForeignKey(Rank)
    member = models.ForeignKey(Member, related_name='membershipPeriods')
    activeFromDate = models.DateTimeField(default=datetime.datetime.utcnow())
    activeToDate = models.DateTimeField(default=datetime.datetime.utcnow())
    lineItem = models.ForeignKey(RankLineItem)

def create_member(sender, instance, created, **kwargs):
  if created:
    Member.objects.get_or_create(user=instance)
    OpenID.objects.get_or_create(user=instance, default=True)

post_save.connect(create_member, sender=User)

def create_rank(sender, instance, created, **kwargs):
  if created:
    Rank.objects.get_or_create(group=instance)

post_save.connect(create_rank, sender=Group)

class AuthenticatedUser(User):
  class Meta:
    proxy = True

  def has_perm(self, perm, obj=None):
    funcLog().debug("Checking %s for permission %s on %r",self, perm, obj)
    if super(AuthenticatedUser, self).has_perm(perm, obj):
      funcLog().debug("Found django permission %s", perm)
      return True
    anon = get_anonymous_user()
    if anon.has_perm(perm, obj):
      funcLog().debug("Found anonymous permission %s", perm)
      return True
    app, perm = perm.split('.', 1)
    ret = get_authenticated_user_group().permissions.filter(
      content_type__app_label = app,
      codename=perm).exists()
    if ret:
      funcLog().debug("Found authenticated group permission %s", perm)
    else:
      funcLog().debug("Denied")
    return ret


class AuthenticatedUserGroup(Group):
  class Meta:
    proxy = True

class AnonymousUser(User):
  def is_anonymous(self):
    return True

  def has_perm(self, *args, **kwargs):
    u = User.objects.get(pk=self.pk)
    return u.has_perm(*args, **kwargs)

  class Meta:
    proxy = True

def get_authenticated_user_group():
  if settings.AUTHENTICATED_GROUP_ID == 0:
    try:
      group = AuthenticatedUserGroup.objects.get(
        name='Authenticated Users'
      )
    except AuthenticatedUserGroup.DoesNotExist:
      group = AuthenticatedUserGroup.objects.create(
        name='Authenticated Users'
      )
  else:
    group = AuthenticatedUserGroup.objects.get(id=settings.AUTHENTICATED_GROUP_ID)
  return group

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
    user = User.objects.get(id=settings.ANONYMOUS_USER_ID)
  try:
    member = user.member
  except Member.DoesNotExist:
    user.member, created = Member.objects.get_or_create(user=user)
    user.save()
  return user

post_save.connect(create_member, sender=AnonymousUser)
