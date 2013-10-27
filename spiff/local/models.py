from django.db import models
from django.db.utils import DatabaseError
from django.contrib.sites.models import Site
from django.db.models.signals import post_save
from spiff.sensors.models import Sensor, SENSOR_TYPE_BOOLEAN

class SpaceConfig(models.Model):
    site = models.OneToOneField(Site)
    logo = models.CharField(max_length=100, default='/logo.png')
    openIcon = models.CharField(max_length=100, blank=True)
    closedIcon = models.CharField(max_length=100, blank=True)
    url = models.CharField(null=True, blank=True, max_length=100)
    open = models.BooleanField(default=False)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    lastChange = models.DateTimeField(auto_now_add=True)
    openSensor = models.ForeignKey(Sensor, null=True, blank=True)
    motd = models.TextField(blank=True)

    def isOpen(self):
        if self.openSensor:
            if self.openSensor.type == SENSOR_TYPE_BOOLEAN:
                return bool(self.openSensor.value())
        return self.open

class SpaceContact(models.Model):
    space = models.ForeignKey('SpaceConfig')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

class SpaceFeed(models.Model):
    space = models.ForeignKey('SpaceConfig')
    name = models.CharField(max_length=100)
    url = models.TextField()

def create_config(sender, instance, created, **kwargs):
  try:
    SpaceConfig.objects.get_or_create(site=instance)
  except DatabaseError: #Happens when we run syncdb and the spaceconfig table doesn't exist yet
    pass

post_save.connect(create_config, sender=Site)
