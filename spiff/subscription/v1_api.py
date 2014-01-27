from tastypie import fields
from tastypie.resources import ModelResource
from spiff.api import SpiffAuthorization
import models

class SubscriptionPeriodResource(ModelResource):
  name = fields.CharField('name')
  dayOfMonth = fields.IntegerField('dayOfMonth')
  monthOfYear = fields.IntegerField('monthOfYear')

  class Meta:
    queryset = models.SubscriptionPeriod.objects.all()
    authorization = SpiffAuthorization()

class SubscriptionPlanResource(ModelResource):
  name = fields.CharField('name')
  period = fields.ToOneField('spiff.subscription.v1_api.SubscriptionPeriodResource',
      'period', full=True)
  periodCost = fields.FloatField('periodCost')

  class Meta:
    querySet = models.SubscriptionPlan.objects.all()
    authorization = SpiffAuthorization()

class SubscriptionResource(ModelResource):
  user = fields.ToOneField('spiff.membership.v1_api.MemberResource',
      'user__member', null=True)
  active = fields.BooleanField('active')
  plan = fields.ToOneField('spiff.subscription.v1_api.SubscriptionPlanResource',
  'plan', full=True)

  class Meta:
    querySet = models.Subscription.objects.all()
    authorization = SpiffAuthorization()

