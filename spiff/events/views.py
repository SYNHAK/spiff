from django.shortcuts import render_to_response
from django.template import RequestContext
import models

def index(request):
  events = models.Event.objects.all()
  return render_to_response('events/index.html',
      {'events': events},
      context_instance=RequestContext(request))

def view(request, id):
  event = models.Event.objects.get(id=id)
  return render_to_response('events/view.html',
      {'event': event},
      context_instance=RequestContext(request))
