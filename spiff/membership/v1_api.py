from django.db.models import Q
from django.conf.urls import url
from django.contrib.auth.models import Group, User
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

class FieldValueAuthorization(SpiffAuthorization):
  def conditions(self):
    return (
      ('public', 'field is public'),
      ('protected', 'field is protected'),
      ('private', 'field is private'),
    ) + super(FieldValueAuthorization, self).conditions()

  def check_perm(self, request, model, permName):
    if model.field.public:
      return super(FieldValueAuthorization, self).check_perm(request, model,
      '%s_public'%(permName))
    if model.field.protected:
      return super(FieldValueAuthorization, self).check_perm(request, model,
      '%s_protected'%(permName))
    return super(FieldValueAuthorization, self).check_perm(request, model,
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

class FieldValueResource(ModelResource):
  field = fields.ToOneField(FieldResource, 'field', full=True)
  value = fields.CharField('value')
  member = fields.ToOneField('spiff.membership.v1_api.MemberResource',
  'member')

  class Meta:
    queryset = models.FieldValue.objects.all()
    authorization = FieldValueAuthorization()

class RankPlanAuthorization(SpiffAuthorization):
  def conditions(self):
    return (
      ('active_membership', 'rank is active membership'),
    )+super(RankPlanAuthorization, self).conditions()

  def check_perm(self, request, model, name):
    if model.rank.isActiveMembership:
      return super(RankPlanAuthorization, self).check_perm(request, model,
        '%s_active_membership'%(name))
    return super(RankPlanAuthorization, self).check_perm(request, model, name)

class RankSubscriptionPlanResource(subscription.SubscriptionPlanResource):
  class Meta:
    queryset = models.RankSubscriptionPlan.objects.all()
    authorization = RankPlanAuthorization()

class RankResource(ModelResource):
  group = fields.ToOneField('spiff.membership.v1_api.GroupResource', 'group')

  class Meta:
    queryset = models.Rank.objects.all()
    authorization = SpiffAuthorization()

class GroupResource(ModelResource):
  rank = fields.ToOneField(RankResource, 'rank', full=True)

  class Meta:
    queryset = Group.objects.all()
    authorization = SpiffAuthorization()

class SelfMemberAuthorization(SpiffAuthorization):
  def check_perm(self, request, model, name):
    if request.user.member.pk == model.pk:
      return True
    return super(SelfMemberAuthorization, self).check_perm(request, model, name)

class SelfUserAuthorization(SpiffAuthorization):
  def check_perm(self, request, model, name):
    funcLog().info("Checking if %s == %s", request.user, model)
    if request.user.pk == model.pk:
      return True
    return super(SelfUserAuthorization, self).check_perm(request, model, name)

class UserResource(ModelResource):
  class Meta:
    queryset = User.objects.all()
    authorization = SelfUserAuthorization()

class MembershipPeriodResource(ModelResource):
  group = fields.ToOneField(GroupResource, 'rank__group', full=True)
  member = fields.ToOneField('spiff.membership.v1_api.MemberResource',
  'member')
  start = fields.DateTimeField('activeFromDate')
  end = fields.DateTimeField('activeToDate')

  class Meta:
    queryset = models.MembershipPeriod.objects.all()
    authorization = SpiffAuthorization()

class MemberResource(ModelResource):
  username = fields.CharField(attribute='user__username')
  firstName = fields.CharField(attribute='user__first_name', null=True)
  lastName = fields.CharField(attribute='user__last_name')
  isAnonymous = fields.BooleanField(attribute='isAnonymous')
  email = fields.CharField(attribute='user__email')
  groups = fields.ToManyField(GroupResource, 'user__groups', null=True,
      full=True)
  outstandingBalance = fields.FloatField('outstandingBalance')
  membershipExpiration = fields.DateTimeField('membershipExpiration', null=True)
  invoices = fields.ToManyField('spiff.payment.v1_api.InvoiceResource', 'user__invoices', null=True)
  subscriptions = fields.ToManyField('spiff.subscription.v1_api.SubscriptionResource', 'user__subscriptions', null=True, full=True)
  stripeCards = fields.ListField(attribute='stripeCards', default=[],
      readonly=True)
  userid = fields.IntegerField('user_id', readonly=True)

  class Meta:
    queryset = models.Member.objects.all()
    authorization = SelfMemberAuthorization()
    filtering = {
      'groups': ('in',)
    }

  def obj_create(self, bundle, **kwargs):
    data = bundle.data
    firstName = ""
    lastName = ""
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
          'token': jwt.encode(token, settings.SECRET_KEY)
        })
      else:
        funcLog().warning("Good login, but %s is disabled.", username)
        raise ImmediateHttpResponse(response=HttpForbidden())
    else:
      funcLog().warning("Invalid login for %s", username)
      raise ImmediateHttpResponse(response=HttpUnauthorized())

