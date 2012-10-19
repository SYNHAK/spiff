from django.template import RequestContext
from django.shortcuts import render_to_response

def index(request):
  if request.user.is_anonymous():
    return render_to_response('local/index_anonymous.html',
        context_instance=RequestContext(request))
  else:
    return render_to_response('local/index.html',
        context_instance=RequestContext(request))
