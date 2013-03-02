from django.template import RequestContext
from django_openid_auth.models import UserOpenID
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from openid_provider.models import TrustedRoot
from spiff.sensors.models import SENSOR_TYPES, Sensor
import json
from django.contrib.sites.models import get_current_site
from django.db.models import Q
from django.shortcuts import render_to_response
from django.forms.models import modelformset_factory
import forms
from spiff.membership.forms import ProfileForm
from spiff.membership.models import FieldValue, Field, Member, Rank
from spiff.events.models import Event
from spiff.local.models import SpaceConfig, SpaceContact, SpaceFeed
from spiff.inventory.models import Resource, Metadata
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
import datetime

def index(request):
  now = datetime.datetime.utcnow()
  events = Event.objects.filter(end__gte=now)
  if request.user.is_anonymous():
    return render_to_response('local/index_anonymous.html',
        {'events': events},
        context_instance=RequestContext(request))
  else:
    return render_to_response('local/index.html',
        {'events': events},
        context_instance=RequestContext(request))

def register(request):
  fields = Field.objects.filter(required=True)
  if request.method == 'POST':
    userForm = forms.RegistrationForm(request.POST, prefix='user')
    profileForm = ProfileForm(request.POST, fields=fields, prefix='profile')
  else:
    userForm = forms.RegistrationForm(prefix='user')
    profileForm = ProfileForm(fields=fields, prefix='profile')
  if userForm.is_valid() and profileForm.is_valid():
    oldUser = None
    try:
      oldUser = User.objects.get(username__exact=userForm.cleaned_data['username'])
    except ObjectDoesNotExist, e:
      pass
    if not oldUser:
      user = User.objects.create_user(userForm.cleaned_data['username'],
          userForm.cleaned_data['email'], userForm.cleaned_data['password'])
      user.first_name = userForm.cleaned_data['firstName']
      user.last_name = userForm.cleaned_data['lastName']
      user.save()
      member = user.member
      member.profession = userForm.cleaned_data['profession']
      member.save()
      user = authenticate(username=userForm.cleaned_data['username'], password=userForm.cleaned_data['password'])
      login(request, user)
      messages.info(request, "Welcome!")
      for field in fields:
        value = FieldValue.objects.create(field=field,
            value=profileForm.fieldValue(field), member=member)
      return HttpResponseRedirect(reverse('home'))
  return render_to_response('local/register.html',
      {'userForm': userForm, 'profileForm':
        profileForm},
      context_instance=RequestContext(request))

def search(request):
  if "query" in request.GET:
    searchForm = forms.SearchForm(request.GET)
  else:
    searchForm = forms.SearchForm()
  if searchForm.is_valid():
    resources = Resource.objects.filter(
      name__iregex='.*%s.*'%(searchForm.cleaned_data['query'])
    )
    metadata = Metadata.objects.filter(
        value__iregex='.*%s.*'%(searchForm.cleaned_data['query'])
    )
    members = Member.objects.filter(
      Q(user__username__iregex='.*%s.*'%(searchForm.cleaned_data['query'])) |
      Q(user__first_name__iregex='.*%s.*'%(searchForm.cleaned_data['query'])) |
      Q(user__last_name__iregex='.*%s.*'%(searchForm.cleaned_data['query']))
    )
  return render_to_response('local/search.html',
      {'resources': resources, 'members': members, 'metadata': metadata},
      context_instance=RequestContext(request))

def spaceapi(request):
  meta = {}
  meta['api'] = '0.12'
  meta['x-spiff-version'] = '0.1'
  site = get_current_site(request)
  base = "%s://%s"%(request.META['wsgi.url_scheme'], site.domain)
  if (request.META['wsgi.url_scheme'] == 'http' and request.META['SERVER_PORT'] != '80') or (request.META['wsgi.url_scheme'] == 'https' and request.META['SERVER_PORT'] != '443'):
    base = "%s:%s"%(base, request.META['SERVER_PORT'])
  meta['x-spiff-url'] = "%s%s"%(base, reverse('home'))

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

@login_required
def untrust_openid_root(request, id):
  root = TrustedRoot.objects.get(id=id)
  if root.openid.user == request.user:
    messages.info(request, "%s was deleted."%(root.trust_root))
    root.delete()
    return HttpResponseRedirect(reverse('home'))
  else:
    raise PermissionDenied()

@login_required
def unassociate_openid(request, id):
  id = UserOpenID.objects.get(id=id)
  if id.user == request.user:
    messages.info(request, "%s was removed."%(id.display_id))
    id.delete()
    return HttpResponseRedirect(reverse('home'))
  else:
    raise PermissionDenied()
