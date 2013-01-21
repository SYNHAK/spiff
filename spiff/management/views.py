from django.core.exceptions import PermissionDenied
from django.template import RequestContext
from django.shortcuts import render_to_response

def index(request):
  if request.user.is_staff:
    return render_to_response('management/index.html',
      context_instance=RequestContext(request))
