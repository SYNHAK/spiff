from django.db import models

SENSOR_TYPE_BOOLEAN = 5 

SENSOR_TYPES = (
  (0, 'number'),
  (1, 'string'),
  (2, 'binary'),
  (3, 'json'),
  (4, 'temp'),
  (SENSOR_TYPE_BOOLEAN, 'boolean'),
)

class Sensor(models.Model):
  name = models.CharField(max_length=255)
  description = models.TextField()
  type = models.IntegerField(choices=SENSOR_TYPES)

  def serialize(self):
    return {
      'value': self.value(),
      'name': self.name,
      'id': self.id,
      'description': self.description,
      'type': SENSOR_TYPES[self.type],
    }

  def valueObj(self):
    v = self.values.all()
    if len(v):
      return v[0]
    return None

  def value(self):
      lastVal = self.valueObj()
      if lastVal:
        if self.type == SENSOR_TYPE_BOOLEAN:
          if lastVal.value.lower() == "false" or lastVal.value == "0" or len(lastVal.value) == 0:
            return False
          return True
        return lastval.value
      return None

  @models.permalink
  def get_absolute_url(self):
    return ('sensors:view', [], {'id': self.id})

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
