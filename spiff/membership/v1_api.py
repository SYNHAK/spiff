from django.db.models import Q
from django.conf.urls import url
from django.contrib.auth.models import Group, User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
import models

class RankResource(ModelResource):
  group = fields.ToOneField('spiff.membership.v1_api.GroupResource', 'group')

  class Meta:
    queryset = models.Rank.objects.all()

class GroupResource(ModelResource):
  rank = fields.ToOneField(RankResource, 'rank', full=True)

  class Meta:
    queryset = Group.objects.all()

class MemberResource(ModelResource):
  firstName = fields.CharField(attribute='user__first_name')
  lastName = fields.CharField(attribute='user__last_name')
  isAnonymous = fields.BooleanField(attribute='user__is_anonymous')
  email = fields.CharField(attribute='user__email')
  groups = fields.ToManyField(GroupResource, 'user__groups', null=True,
      full=True)
  outstandingBalance = fields.FloatField('outstandingBalance')
  membershipExpiration = fields.DateTimeField('membershipExpiration', null=True)
  invoices = fields.ToManyField('spiff.payment.v1_api.InvoiceResource', 'user__invoices', null=True)

  def obj_get(self, bundle, **kwargs):
    if kwargs['pk'] == 'self':
      if bundle.request.user.is_anonymous():
        raise ImmediateHttpResponse(response=HttpUnauthorized());
      else:
        return bundle.request.user.member
    else:
      return Member.objects.get(pk=kwargs['pk'])

  class Meta:
    queryset = models.Member.objects.all()
    authorization = DjangoAuthorization()

  def self(self, request, **kwargs):
    self.method_check(request, allowed=['get'])
    self.throttle_check(request)
    return self.create_response(request, {'objects': [request.user.member]})

  def has_permission(self, request, permission_name, **kwargs):
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
      url(r'^(?P<resource_name>%s)/self/has_permission/(?P<permission_name>.*)%s$' %
        (self._meta.resource_name, trailing_slash()),
        self.wrap_view('has_permission'), name='self_has_permission')
    ]

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
    if request.user and request.user.is_authenticated():
      logout(request)
      return self.create_response(request, {'success': True})
    else:
      return self.create_response(request, {'success': False})
