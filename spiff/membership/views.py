from django.template import RequestContext
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
import models

def index(request):
  users = User.objects.filter(is_active=True)
  return render_to_response('membership/index.html',
      {'users': users},
      context_instance=RequestContext(request))

def view(request, username):
  user = User.objects.get(username=username)
  return render_to_response('membership/view.html',
      {'viewUser': user},
      context_instance=RequestContext(request))
