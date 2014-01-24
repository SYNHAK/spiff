from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource
import models

class SensorResource(ModelResource):
  name = fields.CharField('name')
  description = fields.CharField('description')
  type = fields.IntegerField('type')
  ttl = fields.IntegerField('ttl')
  value = fields.CharField('value')

  class Meta:
    queryset = models.Sensor.objects.all()
    authorization = DjangoAuthorization()
