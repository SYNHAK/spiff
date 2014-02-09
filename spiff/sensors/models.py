from django.db import models
from django.db.models.signals import post_save
import stat
import tempfile
import socket
import requests

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
  ttl = models.IntegerField(default=255)

  def serialize(self):
    return {
      'value': self.value(),
      'name': self.name,
      'id': self.id,
      'description': self.description,
      'type': SENSOR_TYPES[self.type],
      'ttl': self.ttl
    }

  def valueObj(self):
    ret = None
    v = self.values.all()
    if len(v):
      ret = v[0]
    return ret

  def value(self):
      lastVal = self.valueObj()
      if lastVal:
        if self.type == SENSOR_TYPE_BOOLEAN:
          if lastVal.value.lower() == "false" or lastVal.value == "0" or len(lastVal.value) == 0:
            return False
          return True
        return lastVal.value
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

ACTION_HTTP = 0
ACTION_EXEC = 1
ACTION_PYTHON = 2
ACTION_SCRIPT = 3

ACTION_TYPES = (
  (ACTION_HTTP, 'http'),
  (ACTION_EXEC, 'exec'),
  (ACTION_PYTHON, 'python'),
  (ACTION_SCRIPT, 'script'),
)

class Action(models.Model):
  sensor = models.ForeignKey(Sensor, related_name='actions')
  name = models.CharField(max_length=255)
  type = models.IntegerField(choices=ACTION_TYPES)
  value = models.TextField()

  def run(self):
    if self.type == ACTION_HTTP:
      requests.get(self.value)
    if self.type == ACTION_EXEC:
      subprocess.call(self.value.split(" "))
    if self.type == ACTION_PYTHON:
      exec(self.value, {'sensor': self.sensor})
    if self.type == ACTION_SCRIPT:
      (fh, tmp) = tempfile.mkstemp()
      f = os.fdopen(fh)
      f.write(self.value)
      f.close()
      os.chmod(tmp, stat.S_IXUSR | stat.S_IRUSR)
      subprocess.call([tmp,])

def exec_sensor_actions(sender, instance, created, **kwargs):
  if created:
    for action in instance.sensor.actions.all():
      try:
        action.run()
      except Exception, e:
        print e

post_save.connect(exec_sensor_actions, sender=SensorValue)

def flush_old_values(sender, instance, created, **kwargs):
  oldValues = instance.sensor.values.extra(order_by=['stamp'])
  if len(oldValues) > instance.sensor.ttl:
    for v in oldValues[0:len(oldValues)-instance.sensor.ttl]:
      v.delete()

post_save.connect(flush_old_values, sender=SensorValue)
