from tastypie import fields
from tastypie.resources import ModelResource
from spiff.api import SpiffAuthorization
import models
from spiff import funcLog
import json

class SensorUpdateAuthorization(SpiffAuthorization):
  def operations(self):
    return super(SensorUpdateAuthorization, self).operations()+(
      ('update_value_on', 'update_value_on'),
    )

  def check_perm(self, bundle, model, permName):
    if 'value' in bundle.data:
      return super(SensorUpdateAuthorization, self).check_perm(bundle, model,
          'update_value_on_%s'%(permName))
    return super(SensorUpdateAuthorization, self).check_perm(bundle, model, permName)

class SensorResource(ModelResource):
  name = fields.CharField('name')
  description = fields.CharField('description')
  type = fields.IntegerField('type')
  ttl = fields.IntegerField('ttl')
  value = fields.CharField('value')

  class Meta:
    queryset = models.Sensor.objects.all()
    authorization = SensorUpdateAuthorization()
    always_return_data = True

class SensorValueResource(ModelResource):
  sensor = fields.ToOneField(SensorResource, 'sensor')
  value = fields.CharField('value')
  stamp = fields.DateTimeField('stamp')

  class Meta:
    queryset = models.SensorValue.objects.all()
    authorization = SpiffAuthorization()
    always_return_data = True
