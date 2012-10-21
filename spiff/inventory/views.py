from django.template import RequestContext
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
import models

def index(request):
  resources = models.Resource.objects.all()
  return render_to_response('inventory/index.html',
      {'resources': resources},
      context_instance=RequestContext(request))

def view(request, id):
  resource = models.Resource.objects.get(pk=id)
  return render_to_response('inventory/view.html', {'item':resource},
      context_instance=RequestContext(request))

def addMeta(request, id):
  resource = models.Resource.objects.get(pk=id)
  return render_to_response('inventory/addMeta.html', {'item':resource},
      context_instance=RequestContext(request))

def train(request, id):
  resource = models.Resource.objects.get(pk=id)
  return render_to_response('inventory/train.html', {'item':resource},
      context_instance=RequestContext(request))
