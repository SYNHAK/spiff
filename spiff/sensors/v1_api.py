from tastypie import fields
from tastypie.resources import ModelResource
from spiff.api import SpiffAuthorization
import models
from spiff import funcLog

class SensorResource(ModelResource):
  name = fields.CharField('name')
  description = fields.CharField('description')
  type = fields.IntegerField('type')
  ttl = fields.IntegerField('ttl')
  value = fields.CharField('value')

  class Meta:
    queryset = models.Sensor.objects.all()
    authorization = SpiffAuthorization()
    always_return_data = True

class SensorValueResource(ModelResource):
  sensor = fields.ToOneField(SensorResource, 'sensor')
  value = fields.CharField('value')
  stamp = fields.DateTimeField('stamp')

  class Meta:
    queryset = models.SensorValue.objects.all()
    authorization = SpiffAuthorization()
    always_return_data = True
