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
    if 'value' in bundle.data and permName == 'update':
      funcLog("updating perm via %s", permName)
      return super(SensorUpdateAuthorization, self).check_perm(bundle, model,
          'update_value_on')
    return super(SensorUpdateAuthorization, self).check_perm(bundle, model, permName)

class SensorValueField(fields.ApiField):
  dehydrated_type = 'variant'
  help_text = 'A variable type of data, based on another field which specifies the type'

  def __init__(self, *args, **kwargs):
    if 'typeAttr' not in kwargs:
      kwargs['typeAttr'] = 'type'
    self._typeAttr = kwargs['typeAttr']
    del kwargs['typeAttr']
    super(SensorValueField, self).__init__(*args, **kwargs)

  def dehydrate(self, bundle, for_list=False):
    value = super(SensorValueField, self).dehydrate(bundle, for_list)
    if value is None:
      return value

    typeField = getattr(bundle.obj, self._typeAttr)
    if typeField == models.SENSOR_TYPE_NUMBER:
      return int(value)
    if typeField == models.SENSOR_TYPE_STRING:
      return str(value)
    if typeField == models.SENSOR_TYPE_BINARY:
      return str(value)
    if typeField == models.SENSOR_TYPE_JSON:
      return json.loads(value)
    if typeField == models.SENSOR_TYPE_TEMPERATURE:
      return float(value)
    if typeField == models.SENSOR_TYPE_BOOLEAN:
      return bool(value)

  def hydrate(self, bundle):
    value = super(SensorValueField, self).hydrate(bundle)

    typeField = getattr(bundle.obj, self._typeAttr)

    if typeField == models.SENSOR_TYPE_NUMBER:
      return int(value)
    if typeField == models.SENSOR_TYPE_STRING:
      return str(value)
    if typeField == models.SENSOR_TYPE_BINARY:
      return value
    if typeField == models.SENSOR_TYPE_JSON:
      return json.loads(value)
    if typeField == models.SENSOR_TYPE_TEMPERATURE:
      return float(value)
    if typeField == models.SENSOR_TYPE_BOOLEAN:
      return bool(value)


class SensorResource(ModelResource):
  name = fields.CharField('name')
  description = fields.CharField('description')
  type = fields.IntegerField('type')
  ttl = fields.IntegerField('ttl')
  value = SensorValueField('value', 'type')

  def obj_update(self, bundle, **kwargs):
    if 'value' in bundle.data:
      models.SensorValue.objects.create(
        sensor = bundle.obj,
        value = bundle.data['value']
      )
    return super(SensorResource, self).obj_update(bundle, **kwargs)

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
