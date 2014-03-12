from tastypie import fields
from tastypie.resources import ModelResource
from spiff.api import SpiffAuthorization, OwnedObjectAuthorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
import models

class SubscriptionPeriodResource(ModelResource):
  name = fields.CharField('name')
  dayOfMonth = fields.IntegerField('dayOfMonth')
  monthOfYear = fields.IntegerField('monthOfYear')

  class Meta:
    queryset = models.SubscriptionPeriod.objects.all()
    authorization = SpiffAuthorization()
    filtering = {
      'name': ALL_WITH_RELATIONS,
      'dayOfMonth': ALL_WITH_RELATIONS,
      'monthOfYear': ALL_WITH_RELATIONS
    }

class SubscriptionPlanResource(ModelResource):
  name = fields.CharField('name')
  period = fields.ToOneField('spiff.subscription.v1_api.SubscriptionPeriodResource',
      'period', full=True)
  periodCost = fields.FloatField('periodCost')

  class Meta:
    queryset = models.SubscriptionPlan.objects.all()
    authorization = SpiffAuthorization()
    filtering = {
      'name': ALL_WITH_RELATIONS,
      'period': ALL_WITH_RELATIONS,
      'periodCost': ALL_WITH_RELATIONS
    }

class SubscriptionResource(ModelResource):
  user = fields.ToOneField('spiff.membership.v1_api.UserResource',
      'user', null=True)
  active = fields.BooleanField('active')
  plan = fields.ToOneField('spiff.subscription.v1_api.SubscriptionPlanResource',
  'plan', full=True)

  class Meta:
    queryset = models.Subscription.objects.all()
    authorization = OwnedObjectAuthorization('user')
    always_return_data = True
    filtering = {
      'user': ALL_WITH_RELATIONS,
      'active': ALL_WITH_RELATIONS,
      'plan': ALL_WITH_RELATIONS
    }
