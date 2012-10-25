from django.template import RequestContext
from django.db.models import Q
from django.shortcuts import render_to_response
from django.forms.models import modelformset_factory
import forms
from spiff.membership.forms import ProfileForm
from spiff.membership.models import FieldValue, Field, Member
from spiff.events.models import Event
from spiff.inventory.models import Resource
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import datetime

def index(request):
  now = datetime.datetime.now()
  events = Event.objects.filter(end__gt=now)
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
      member.birthday = userForm.cleaned_data['birthday']
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
      Q(name__iregex='.*%s.*'%(searchForm.cleaned_data['query'])) |
      Q(metadata__value__iregex='.*%s.*'%(searchForm.cleaned_data['query']))
    )
    members = Member.objects.filter(
      Q(user__username__iregex='.*%s.*'%(searchForm.cleaned_data['query'])) |
      Q(user__first_name__iregex='.*%s.*'%(searchForm.cleaned_data['query'])) |
      Q(user__last_name__iregex='.*%s.*'%(searchForm.cleaned_data['query'])) |
      Q(attributes__value__iregex='.*%s.*'%(searchForm.cleaned_data['query']))
    )
  return render_to_response('local/search.html',
      {'resources': resources, 'members': members},
      context_instance=RequestContext(request))
