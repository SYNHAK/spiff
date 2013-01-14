from django.db import models
from django.contrib.sites.models import Site
from django.db.models.signals import post_save

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

class SpaceContact(models.Model):
    space = models.ForeignKey('SpaceConfig')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

class SpaceFeed(models.Model):
    space = models.ForeignKey('SpaceConfig')
    name = models.CharField(max_length=100)
    url = models.TextField()

def create_config(sender, instance, created, **kwargs):
  SpaceConfig.objects.get_or_create(site=instance)

post_save.connect(create_config, sender=Site)
