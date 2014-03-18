from django.db.models import Q
from django.utils.timezone import utc
import datetime
from django.contrib.sites.models import get_current_site
import string
import random
from django.conf.urls import url
from django.contrib.auth.models import Group, User, Permission
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from tastypie import fields
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
import models
from spiff.api import SpiffAuthorization
import json
from spiff.subscription import v1_api as subscription
from spiff import funcLog
import jwt
from django.conf import settings
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from django.core.mail import send_mail

class FieldValueAuthorization(SpiffAuthorization):
  def conditions(self):
    return (
      ('public', 'field is public'),
      ('protected', 'field is protected'),
      ('private', 'field is private'),
    ) + super(FieldValueAuthorization, self).conditions()

  def check_perm(self, bundle, model, permName):
    if model.field.public:
      return super(FieldValueAuthorization, self).check_perm(bundle, model,
      '%s_public'%(permName))
    if model.field.protected:
      return super(FieldValueAuthorization, self).check_perm(bundle, model,
      '%s_protected'%(permName))
    return super(FieldValueAuthorization, self).check_perm(bundle, model,
    '%s_private'%(permName))

class FieldResource(ModelResource):
  name = fields.CharField('name')
  description = fields.CharField('description')
  required = fields.BooleanField('required')
  public = fields.BooleanField('public')
  protected = fields.BooleanField('protected')

  class Meta:
    queryset = models.Field.objects.all()
    authorization = SpiffAuthorization()
    always_return_data = True

class FieldValueResource(ModelResource):
  field = fields.ToOneField(FieldResource, 'field', full=True)
  value = fields.CharField('value')
  member = fields.ToOneField('spiff.membership.v1_api.MemberResource',
  'member')

  class Meta:
    queryset = models.FieldValue.objects.all()
    authorization = FieldValueAuthorization()
    always_return_data = True

class RankPlanAuthorization(SpiffAuthorization):
  def conditions(self):
    return (
      ('active_membership', 'rank is active membership'),
    )+super(RankPlanAuthorization, self).conditions()

  def check_perm(self, bundle, model, name):
    if model.rank.isActiveMembership:
      return super(RankPlanAuthorization, self).check_perm(bundle, model,
        '%s_active_membership'%(name))
    return super(RankPlanAuthorization, self).check_perm(bundle, model, name)

class RankSubscriptionPlanResource(subscription.SubscriptionPlanResource):
  class Meta:
    queryset = models.RankSubscriptionPlan.objects.all()
    authorization = RankPlanAuthorization()
    always_return_data = True

class RankResource(ModelResource):
  group = fields.ToOneField('spiff.membership.v1_api.GroupResource', 'group')
  monthlyDues = fields.FloatField('monthlyDues')
  isActiveMembership = fields.BooleanField('isActiveMembership')

  class Meta:
    queryset = models.Rank.objects.all()
    authorization = SpiffAuthorization()
    always_return_data = True
    filtering = {
      'group': ALL_WITH_RELATIONS,
      'monthlyDues': ALL_WITH_RELATIONS,
      'isActiveMembership': ALL_WITH_RELATIONS
    }

class PermissionResource(ModelResource):
  name = fields.CharField('name', readonly=True)
  app = fields.CharField('content_type__app_label', readonly=True)
  codename = fields.CharField('codename', readonly=True)
  id = fields.IntegerField('id', readonly=True)

  class Meta:
    queryset = Permission.objects.all()
    authorization = SpiffAuthorization()
    always_return_data = True
    filtering = {
      'id': ALL_WITH_RELATIONS,
      'name': ALL_WITH_RELATIONS,
      'app': ALL_WITH_RELATIONS,
      'codename': ALL_WITH_RELATIONS
    }

class GroupResource(ModelResource):
  rank = fields.ToOneField(RankResource, 'rank', full=True)
  permissions = fields.ToManyField(PermissionResource, 'permissions', full=False)

  class Meta:
    queryset = Group.objects.all()
    authorization = SpiffAuthorization()
    always_return_data = True
    filtering = {
      'rank': ALL_WITH_RELATIONS,
      'name': ALL_WITH_RELATIONS,
      'permissions': ALL_WITH_RELATIONS
    }

class SelfMemberAuthorization(SpiffAuthorization):
  def check_perm(self, bundle, model, name):
    if bundle.request.user.member.pk == model.pk:
      return True
    return super(SelfMemberAuthorization, self).check_perm(bundle, model, name)

class SelfUserAuthorization(SpiffAuthorization):
  def check_perm(self, bundle, model, name):
    funcLog().info("Checking if %s == %s", bundle.request.user, model)
    if bundle.request.user.pk == model.pk:
      return True
    return super(SelfUserAuthorization, self).check_perm(bundle, model, name)

class UserResource(ModelResource):
  permissions = fields.ToManyField(PermissionResource, 'user_permissions',
      full=False)

  class Meta:
    queryset = User.objects.all()
    authorization = SelfUserAuthorization()
    always_return_data = True
    filtering = {
      'first_name': ALL_WITH_RELATIONS,
      'last_name': ALL_WITH_RELATIONS,
      'permissions': ALL_WITH_RELATIONS
    }

class MembershipPeriodResource(ModelResource):
  rank = fields.ToOneField(RankResource, 'rank', full=True)
  member = fields.ToOneField('spiff.membership.v1_api.MemberResource',
  'member')
  activeFromDate = fields.DateTimeField('activeFromDate')
  activeToDate = fields.DateTimeField('activeToDate')
  contiguousPeriods = fields.ToManyField('spiff.membership.v1_api.MembershipPeriodResource', 'contiguousPeriods', null=True)
  contiguousDates = fields.ListField('contiguousDates', null=True)

  class Meta:
    queryset = models.MembershipPeriod.objects.all()
    authorization = SpiffAuthorization()
    always_return_data = True
    filtering = {
      'rank': ALL_WITH_RELATIONS,
      'member': ALL_WITH_RELATIONS,
      'activeFromDate': ALL_WITH_RELATIONS,
      'activeToDate': ALL_WITH_RELATIONS
    }

class MemberResource(ModelResource):
  user = fields.ToOneField(UserResource, 'user', full=False)
  username = fields.CharField(attribute='user__username')
  firstName = fields.CharField(attribute='user__first_name', null=True)
  lastName = fields.CharField(attribute='user__last_name')
  activeMember = fields.BooleanField(attribute='activeMember',
      readonly=True)
  isAnonymous = fields.BooleanField(attribute='isAnonymous')
  email = fields.CharField(attribute='user__email')
  groups = fields.ToManyField(GroupResource, 'user__groups', null=True,
      full=True)
  outstandingBalance = fields.FloatField('outstandingBalance')
  invoices = fields.ToManyField('spiff.payment.v1_api.InvoiceResource', 'user__invoices', null=True)
  subscriptions = fields.ToManyField('spiff.subscription.v1_api.SubscriptionResource', 'user__subscriptions', null=True, full=True)
  stripeCards = fields.ListField(attribute='stripeCards', default=[],
      readonly=True)
  userid = fields.IntegerField('user_id', readonly=True)
  membershipRanges = fields.ListField('membershipRanges', null=True)
  availableCredit = fields.FloatField('availableCredit')
  fields = fields.ToManyField('spiff.membership.v1_api.FieldValueResource', 'attributes', full=False, null=True)

  class Meta:
    queryset = models.Member.objects.all()
    authorization = SelfMemberAuthorization()
    always_return_data = True
    filtering = {
      'groups': ALL_WITH_RELATIONS,
      'firstName': ALL_WITH_RELATIONS,
      'lastName': ALL_WITH_RELATIONS,
    }

  def obj_update(self, bundle, **kwargs):
    data = bundle.data
    if 'currentPassword' in data and 'password' in data:
      u = bundle.obj.user
      valid = False
      if u.check_password(data['currentPassword']):
        valid = True
      else:
        tokens = models.UserResetToken.objects.filter(user=u,
            token=data['currentPassword'])
        if tokens.exists():
          valid = True
      u.set_password(data['password'])
      u.save()
    return bundle

  def obj_create(self, bundle, **kwargs):
    data = bundle.data
    firstName = ""
    lastName = ""
    funcLog().debug("Creating user from %r", data)
    if 'firstName' in data:
      firstName = data['firstName']
    if 'lastName' in data:
      lastName = data['lastName']
    u = User.objects.create(
      username = data['username'],
      email = data['email'],
      first_name = firstName,
      last_name = lastName
    )
    u.set_password(data['password'])
    u.save()
    if 'fields' in data:
      for f in data['fields']:
        field = models.Field.objects.get(id=f['id'])
        models.FieldValue.objects.create(
          field = field,
          value = f['value'],
          member = u.member
        )
    bundle.obj = u.member
    return bundle

  def self(self, request, **kwargs):
    self.method_check(request, allowed=['get'])
    self.throttle_check(request)
    return self.get_detail(request, pk=request.user.member.id)

  def has_permission(self, request, permission_name, **kwargs):
    if permission_name == 'is_superuser' and request.user.is_superuser:
      return HttpResponse(status=204)
    if request.user.has_perm(permission_name):
      return HttpResponse(status=204)
    return HttpResponse(status=403)

  def prepend_urls(self):
    return [
      url(r'^(?P<resource_name>%s)/login%s$' %
        (self._meta.resource_name, trailing_slash()),
        self.wrap_view('login'), name='login'),
      url(r'^(?P<resource_name>%s)/requestPasswordReset%s$' %
        (self._meta.resource_name, trailing_slash()),
        self.wrap_view('requestPasswordReset'), name='requestPasswordReset'),
      url(r'^(?P<resource_name>%s)/search%s$' %
        (self._meta.resource_name, trailing_slash()),
        self.wrap_view('search'), name='search'),
      url(r'^(?P<resource_name>%s)/self%s$' %
        (self._meta.resource_name, trailing_slash()),
        self.wrap_view('self'), name='self'),
      url(r'^(?P<resource_name>%s)/(?P<id>.*)/stripeCards/(?P<stripeCardID>.*)%s$' %
        (self._meta.resource_name, trailing_slash()),
        self.wrap_view('stripeCard'), name='self'),
      url(r'^(?P<resource_name>%s)/(?P<id>.*)/stripeCards%s$' %
        (self._meta.resource_name, trailing_slash()),
        self.wrap_view('stripeCards'), name='self'),
      url(r'^(?P<resource_name>%s)/self/has_permission/(?P<permission_name>.*)%s$' %
        (self._meta.resource_name, trailing_slash()),
        self.wrap_view('has_permission'), name='self_has_permission')
    ]

  def stripeCards(self, request, **kwargs):
    self.method_check(request, allowed=['post', 'get'])
    self.is_authenticated(request)
    self.throttle_check(request)
    member = models.Member.objects.get(pk=kwargs['id'])

    if request.method == 'POST':
      cardData = json.loads(request.body)
      newCard = {}
      newCard['number'] = cardData['card']
      newCard['exp_month'] = cardData['exp_month']
      newCard['exp_year'] = cardData['exp_year']
      newCard['cvc'] = cardData['cvc']
      member.addStripeCard(newCard)

      return self.create_response(request, {'success': True})
    else:
      return self.create_response(request, {'cards': member.stripeCards})

  def stripeCard(self, request, **kwargs):
    self.method_check(request, allowed=['delete'])
    self.is_authenticated(request)
    self.throttle_check(request)

    cardID = kwargs['stripeCardID']

    member = models.Member.objects.get(pk=kwargs['id'])
    member.removeStripeCard(cardID)

    return self.create_response(request, {'success': True})

  def search(self, request, **kwargs):
    self.method_check(request, allowed=['get'])
    self.is_authenticated(request)
    self.throttle_check(request)

    name = request.GET['fullName'].split(' ')
    query = Q()
    if len(name) == 1:
      query &= Q(first_name__icontains=name[0]) | Q(last_name__icontains=name[0])
    else:
      query &= Q(first_name__icontains=name[0]) | Q(last_name__icontains=' '.join(name[1:]))
      firstName, lastName = request.GET['fullName'].split(' ', 1)
    query &= Q(member__hidden=False)
    funcLog().info("User search query: %s", query)
    users = User.objects.filter(query)
    objects = []
    for u in users:
      bundle = self.build_bundle(obj=u.member, request=request)
      bundle = self.full_dehydrate(bundle)
      objects.append(bundle)

    object_list = {'objects': objects}
    return self.create_response(request, object_list)

  def requestPasswordReset(self, request, **kwargs):
    self.method_check(request, allowed=['post'])
    data = self.deserialize(request, request.body,
        format=request.META.get('CONTENT_TYPE', 'application/json'))

    users = User.objects.filter(Q(username=data['userid']) |
      Q(email=data['userid']))

    site = get_current_site(request)

    for u in users:
      token = models.UserResetToken.objects.create(user=u)
      funcLog().info("Resetting password for %s, mailing %s to %s", u.username,
          token.token, u.email)
      message = [
        random.choice(settings.GREETINGS),
        '',
        'This is Spaceman Spiff for %s'%(site.name),
        '',
        'Someone from the IP %s has requested that your password be reset.',
        '',
        'To reset your password, visit %s and use this temporary password to login:'%(settings.WEBUI_URL),
        '',
        '%s'%(token.token),
        '',
        'It will expire after 5 minutes. If you did not request to have your password reset, feel free to ignore this message!'
        '',
        'Thanks!'
      ]

      send_mail('Spiff Password Reset', "\n".join(message), settings.DEFAULT_FROM_EMAIL,
          [u.email])
    return self.create_response(request, {'success': True})

  def login(self, request, **kwargs):
    self.method_check(request, allowed=['post'])
    data = self.deserialize(request, request.body,
        format=request.META.get('CONTENT_TYPE', 'application/json'))

    if 'username' in data and 'password' in data:
      username = data['username']
      password = data['password']
    else:
      username = None
      password = None

    user = authenticate(username=username, password=password)
    if user:
      if user.is_active:
        funcLog().info("Successful login for %s", username)
        token = {}
        token['id'] = user.id
        return self.create_response(request, {
          'success': True,
          'token': jwt.encode(token, settings.SECRET_KEY),
          'passwordReset': False
        })
      else:
        funcLog().warning("Good login, but %s is disabled.", username)
        raise ImmediateHttpResponse(response=HttpForbidden())
    else:
      tokens = models.UserResetToken.objects.filter(user__username=username, token=password)
      for t in tokens:
        if t.created >= datetime.datetime.utcnow().replace(tzinfo=utc)-datetime.timedelta(minutes=5):
          user = t.user
          funcLog().info("Successful password reset for %s", user.username)
          token = {}
          token['id'] = user.id
          return self.create_response(request, {
            'success': True,
            'token': jwt.encode(token, settings.SECRET_KEY),
            'passwordReset': True,
          })
        else:
          t.delete()
      funcLog().warning("Invalid login for %s", username)
      raise ImmediateHttpResponse(response=HttpUnauthorized())

class RankLineItemResource(ModelResource):
  rank = fields.ToOneField(RankResource, 'rank')
  member = fields.ToOneField(MemberResource, 'member')
  activeFromDate = fields.DateField('activeFromDate')
  activeToDate = fields.DateField('activeToDate')
  invoice = fields.ToOneField('spiff.payment.v1_api.InvoiceResource', 'invoice')
  quantity = fields.IntegerField('quantity')

  class Meta:
    queryset = models.RankLineItem.objects.all()
    always_return_data = True
    authorization = SpiffAuthorization()
    filtering = {
      'rank': ALL_WITH_RELATIONS,
      'member': ALL_WITH_RELATIONS,
      'activeFromDate': ALL_WITH_RELATIONS,
      'activeToDate': ALL_WITH_RELATIONS,
      'invoice': ALL_WITH_RELATIONS,
      'quantity': ALL_WITH_RELATIONS
    }
