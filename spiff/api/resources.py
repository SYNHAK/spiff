from spiff.inventory.models import Resource, Metadata, Change, Certification
from django.db.models import Q
from spiff.membership.models import Member, Rank
from django.contrib.auth.models import Group, User
from spiff.payment.models import Invoice, LineItem, Payment
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from tastypie.exceptions import BadRequest, ImmediateHttpResponse
import stripe
from django.conf import settings
from spiff.notification_loader import notification
from tastypie.utils import trailing_slash
from django.conf.urls import url
from django.contrib.auth import authenticate, login, logout
from tastypie.http import HttpUnauthorized

class ResourceMetadataResource(ModelResource):
  name = fields.CharField('name')
  value = fields.CharField('value')
  resource = fields.ToOneField('api.resources.ResourceResource', 'resource')

  class Meta:
    queryset = Metadata.objects.all()

class ResourceResource(ModelResource):
  name = fields.CharField('name')
  metadata = fields.ToManyField(ResourceMetadataResource, 'metadata', full=True)

  class Meta:
    queryset = Resource.objects.all()
    resource_name = 'resource'

class PaymentResource(ModelResource):
  invoice = fields.ToOneField('api.resources.InvoiceResource', 'invoice')
  value = fields.FloatField('value')

  class Meta:
    queryset = Payment.objects.all()
    authorization = Authorization()
    always_return_data = True

  def obj_create(self, bundle, **kwargs):
    bundle = self.full_hydrate(bundle)
    m2m = self.hydrate_m2m(bundle)
    print 'data', bundle.data
    invoice = m2m.obj.invoice
    stripe.api_key = settings.STRIPE_KEY
    cardData = {}
    stripeData = bundle.data['stripe']
    cardData['number'] = stripeData['card']
    cardData['exp_month'] = stripeData['exp_month']
    cardData['exp_year'] = stripeData['exp_year']
    cardData['cvc'] = stripeData['cvc']
    balance = float(bundle.data['value'])
    if balance > invoice.unpaidBalance:
      raise ImmediateHttpResponse(response=self.error_response("You can't pay more than $%s!"%(invoice.unpaidBalance)))
    try:
      charge = stripe.Charge.create(
        amount = int(balance*100),
        currency = 'usd',
        card = cardData,
        description = 'Payment from %s for invoice %s'%(bundle.request.user.member.fullName, invoice.id)
      )
      payment = Payment.objects.create(
        user = bundle.request.user,
        value = balance,
        status = Payment.STATUS_PAID,
        transactionID = charge.id,
        method = Payment.METHOD_STRIPE,
        invoice = invoice
      )
      if notification:
        notification.send(
          [bundle.request.user],
          'payment_received',
          {'user': bundle.request.user, 'payment': payment}
        )
      bundle.obj = payment
    except stripe.CardError, e:
      raise e
    return bundle

class RankResource(ModelResource):
  group = fields.ToOneField('api.resources.GroupResource', 'group')

  class Meta:
    queryset = Rank.objects.all()

class GroupResource(ModelResource):
  rank = fields.ToOneField(RankResource, 'rank', full=True)

  class Meta:
    queryset = Group.objects.all()

class LineItemResource(ModelResource):
  name = fields.CharField(attribute='name')
  unitPrice = fields.FloatField('unitPrice')
  quantity = fields.FloatField('quantity')
  totalPrice = fields.FloatField('totalPrice')

  class Meta:
    querySet = LineItem.objects.all()

class InvoiceResource(ModelResource):
  user = fields.ToOneField('api.resources.MemberResource', 'user__member', null=True, full=True)
  unpaidBalance = fields.FloatField('unpaidBalance')
  paidBalance = fields.FloatField('paidBalance')
  total = fields.FloatField('total')
  items = fields.ToManyField(LineItemResource, 'items', null=True, full=True);
  payments = fields.ToManyField(PaymentResource, 'payments', null=True, full=True);

  class Meta:
    queryset = Invoice.objects.all()

class MemberResource(ModelResource):
  firstName = fields.CharField(attribute='user__first_name')
  lastName = fields.CharField(attribute='user__last_name')
  isAnonymous = fields.BooleanField(attribute='user__is_anonymous')
  email = fields.CharField(attribute='user__email')
  groups = fields.ToManyField(GroupResource, 'user__groups', null=True,
      full=True)
  outstandingBalance = fields.FloatField('outstandingBalance')
  membershipExpiration = fields.DateTimeField('membershipExpiration', null=True)
  invoices = fields.ToManyField(InvoiceResource, 'user__invoices', null=True)

  def obj_get(self, bundle, **kwargs):
    if kwargs['pk'] == 'self':
      if bundle.request.user.is_anonymous():
        raise ImmediateHttpResponse(response=HttpUnauthorized());
      else:
        return bundle.request.user.member
    else:
      return Member.objects.get(pk=kwargs['pk'])

  class Meta:
    queryset = Member.objects.all()

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
        self.wrap_view('search'), name='search')
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
