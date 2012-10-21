from django.template import RequestContext
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_control
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from cStringIO import StringIO
import models
import qrcode

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

@cache_control(public=True, private=False, no_cache=False, no_transform=False, must_revalidate=False, proxy_revalidate=False, max_age=86400)
def qrCode(request, id):
  site = get_current_site(request)
  base = "%s://%s"%(request.META['wsgi.url_scheme'], site.domain)
  if request.META['SERVER_PORT']:
    base = "%s:%s"%(base, request.META['SERVER_PORT'])
  img = qrcode.make("%s%s"%(base,
    reverse('spiff.inventory.views.view', kwargs={'id': id})))
  buf = StringIO()
  img.save(buf, "PNG")
  return HttpResponse(buf.getvalue(), content_type="image/png")
