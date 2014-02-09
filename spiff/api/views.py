from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from spiff.local.models import SpaceConfig, SpaceContact, SpaceFeed
from spiff.membership.models import Rank
from spiff.sensors.models import SENSOR_TYPES, Sensor
import json
import random

def spaceapi(request):
  meta = {}
  meta['api'] = '0.12'
  meta['x-spiff-version'] = '0.1'
  site = get_current_site(request)
  base = "%s://%s"%(request.META['wsgi.url_scheme'], site.domain)
  if (request.META['wsgi.url_scheme'] == 'http' and request.META['SERVER_PORT'] != '80') or (request.META['wsgi.url_scheme'] == 'https' and request.META['SERVER_PORT'] != '443'):
    base = "%s:%s"%(base, request.META['SERVER_PORT'])
  meta['x-spiff-url'] = "%s%s"%(base, reverse('root'))

  spaceConfig = SpaceConfig.objects.get(site=site)

  meta['space'] = site.name
  meta['logo'] = spaceConfig.logo
  meta['icon'] = {'open': spaceConfig.closedIcon, 'closed': spaceConfig.openIcon}
  meta['url'] = site.domain
  meta['open'] = spaceConfig.isOpen()

  if spaceConfig.openSensor is not None:
      meta['x-spiff-open-sensor'] = spaceConfig.openSensor.id

  meta['address'] = spaceConfig.address
  meta['lat'] = spaceConfig.lat
  meta['lon'] = spaceConfig.lon
  meta['status'] = spaceConfig.status
  meta['lastchange'] = str(spaceConfig.lastChange)
  meta['motd'] = spaceConfig.motd
  meta['x-spiff-welcome'] = settings.WELCOME_MESSAGE
  meta['x-spiff-greeting'] = random.choice(settings.GREETINGS)

  contacts = {}
  for c in SpaceContact.objects.filter(space=spaceConfig):
    contacts[c.name] = c.value
  meta['contact'] = contacts

  keyholders = []
  for r in Rank.objects.filter(isKeyholder=True):
    for u in r.group.user_set.all():
      keyholders.append(str(u.member))

  meta['contact']['keymaster'] = keyholders

  feeds = []
  for f in SpaceFeed.objects.filter(space=spaceConfig):
    feeds.append({'name': f.name, 'url': f.url})
  meta['feeds'] = feeds

  sensors = {}
  for t in SENSOR_TYPES:
    sensors[t[1]] = []
    for s in Sensor.objects.filter(type=t[0]):
      v = s.value()
      sensors[t[1]].append({s.name: v})
  meta['sensors'] = sensors

  data = json.dumps(meta, indent=True)
  resp = HttpResponse(data)
  resp['Content-Type'] = 'text/plain'
  return resp

