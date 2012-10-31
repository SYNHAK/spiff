from django.db import models

SENSOR_TYPES = (
  (0, 'number'),
  (1, 'string'),
  (2, 'binary'),
  (3, 'json'),
)

class Sensor(models.Model):
  name = models.CharField(max_length=255)
  description = models.TextField()
  type = models.IntegerField(choices=SENSOR_TYPES)

  def value(self):
    v = self.values.all()
    if len(v):
      return v[0]
    return None

  @models.permalink
  def get_absolute_url(self):
    return ('spiff.sensors.view.view', [], {'id': self.id})

  def __unicode__(self):
    return self.name

class SensorValue(models.Model):
  sensor = models.ForeignKey(Sensor, related_name='values')
  value = models.TextField()
  stamp = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-stamp']

  def __unicode__(self):
    return "%s=%s"%(self.sensor.name, self.value)
