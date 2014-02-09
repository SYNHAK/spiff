from tastypie import fields
from tastypie.resources import ModelResource
from spiff.api import SpiffAuthorization
import models

class SensorResource(ModelResource):
  name = fields.CharField('name')
  description = fields.CharField('description')
  type = fields.IntegerField('type')
  ttl = fields.IntegerField('ttl')
  value = fields.CharField('value')

  class Meta:
    queryset = models.Sensor.objects.all()
    authorization = SpiffAuthorization()
