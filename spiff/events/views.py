from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.template import RequestContext
from spiff.inventory.models import Resource
from spiff.views import ObjectView
import models
import forms

class EventView(ObjectView):
  model = models.Event
  template_name = 'events/view.html'
  index_template_name = 'events/index.html'

def attend(request, id):
  event = models.Event.objects.get(id=id)
  event.attendees.add(request.user.member)
  event.save()
  messages.info(request, "Your planned attendence is duly noted.")
  return HttpResponseRedirect(reverse('events:view', kwargs={'id':
    event.id}))

@permission_required('events.can_reserve_resource')
def addResource(request, id):
  event = models.Event.objects.get(id=id)
  resources = Resource.objects.all()
  if request.method == 'POST':
    picker = forms.ReserveResourceForm(request.POST, resources=resources)
  else:
    picker = forms.ReserveResourceForm(resources=resources)
  if picker.is_valid():
    for resource in resources:
      if picker.resourceIsSelected(resource):
        event.resources.add(resource)
    event.save()
    messages.info(request, "Resources reserved.")
    return HttpResponseRedirect(reverse('events:view', kwargs={'id':
      event.id}))
  return render_to_response('events/addResource.html',
      {'resourceForm': picker, 'event': event},
      context_instance=RequestContext(request))

@permission_required('events.can_add_event')
def create(request):
  if request.method == "POST":
    form = forms.EventForm(request.POST)
  else:
    form = forms.EventForm()
  if form.is_valid():
    event = models.Event.objects.create(
        start = form.cleaned_data['start'],
        end = form.cleaned_data['end'],
        description = form.cleaned_data['description'],
        name = form.cleaned_data['name'],
        creator = request.user.member)
    event.attendees.add(request.user.member)
    event.save()
    messages.info(request, "Event created.")
    return HttpResponseRedirect(reverse('events:view', kwargs={'id':
      event.id}))
  return render_to_response('events/create.html',
      {'eventForm': form},
      context_instance=RequestContext(request))
