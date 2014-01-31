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
from tastypie.exceptions import Unauthorized
import models
from spiff.api import SpiffAuthorization
import json

class FieldValueAuthorization(SpiffAuthorization):
  def check_perm(self, request, model, name, op):
    if model.field.public:
      return super(FieldValueAuthorization, self).check_perm(request, model,
      '%s_public', op)
    if model.field.protected:
      return super(FieldValueAuthorization, self).check_perm(request, model,
      '%s_protected', op)
    return super(FieldValueAuthorization, self).check_perm(request, model,
    '%s_private', op)

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

class RankResource(ModelResource):
  group = fields.ToOneField('spiff.membership.v1_api.GroupResource', 'group')

  class Meta:
    queryset = models.Rank.objects.all()
    authorization = SpiffAuthorization()

class GroupResource(ModelResource):
  rank = fields.ToOneField(RankResource, 'rank', full=True)

  def prepend_urls(self):
    return [
      url(r'^(?P<resource_name>%s)/(?P<group_id>.*)/members%s$' %
        (self._meta.resource_name, trailing_slash()),
        self.wrap_view('get_members'), name='get_members'),
    ]

  def get_members(self, request, group_id, **kwargs):
    group = Group.objects.get(pk=group_id)
    users = User.objects.filter(groups=group)
    objects = []
    for u in users:
      bundle = MemberResource().build_bundle(obj=u.member, request=request)
      bundle = MemberResource().full_dehydrate(bundle)
      objects.append(bundle)
    object_list = {'objects': objects}
    return self.create_response(request, object_list)

  class Meta:
    queryset = Group.objects.all()
    authorization = SpiffAuthorization()

class SelfMemberAuthorization(SpiffAuthorization):
  def check_perm(self, request, model, name, op):
    if request.user.pk == model.pk:
      return True
    return super(SelfMemberAuthorization, self).check_perm(request, model, name,
        op)

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

  class Meta:
    queryset = models.Member.objects.all()
    authorization = SelfMemberAuthorization()

  def obj_create(self, bundle, **kwargs):
    data = bundle.data
    u = User.objects.create(
      username = data['username'],
      email = data['email'],
      first_name = data['firstName'],
      last_name = data['lastName']
    )
    u.set_password(data['password'])
    u.save()
    for f in data['fields']:
      field = models.Field.objects.get(id=f['id'])
      val = models.FieldValue.objects.create(
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
      url(r'^(?P<resource_name>%s)/logout%s$' %
        (self._meta.resource_name, trailing_slash()),
        self.wrap_view('logout'), name='logout'),
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
        login(request, user)
        return self.create_response(request, {'success': True})
      else:
        raise ImmediateHttpResponse(response=HttpForbidden())
    else:
      raise ImmediateHttpResponse(response=HttpUnauthorized())

  def logout(self, request, **kwargs):
    self.method_check(request, allowed=['get'])
    success = False
    if request.user and request.user.is_authenticated():
      logout(request)
      success = True
    return self.create_response(request, {'success': success})
