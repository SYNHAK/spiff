from django.test import TestCase
from spiff.api.tests import APITestMixin, withPermission
import models

class SensorTest(APITestMixin):
  def setUp(self):
    self.setupAPI()
    self.sensor = models.Sensor.objects.create(
      name = 'sensor',
      description = 'Test sensor',
      type = 0,
      ttl = 255
    )

  @withPermission('sensors.read_sensor')
  @withPermission('sensors.update_value_on_sensor')
  def testSetSensorValue(self):
    self.patchAPI('/v1/sensor/%s/'%(self.sensor.id), {
      'value': True,
    })
    self.assertEqual(self.sensor.value(), 'True')
    self.patchAPI('/v1/sensor/%s/'%(self.sensor.id), {
      'value': False,
    })
    self.assertEqual(self.sensor.value(), 'False')

  def testSensorTTL(self):
    for i in range(0, self.sensor.ttl*2):
      models.SensorValue.objects.create(
          sensor=self.sensor,
          value=True
      )
    self.assertEqual(len(self.sensor.values.all()), self.sensor.ttl)
