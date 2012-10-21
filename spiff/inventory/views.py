from django.template import RequestContext
from django.contrib import messages
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_control
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import permission_required
from cStringIO import StringIO
import models
import qrcode
import forms

def index(request):
  resources = models.Resource.objects.all()
  return render_to_response('inventory/index.html',
      {'resources': resources},
      context_instance=RequestContext(request))

def view(request, id):
  resource = models.Resource.objects.get(pk=id)
  return render_to_response('inventory/view.html', {'item':resource},
      context_instance=RequestContext(request))

@permission_required('inventory.can_add_metadata')
def addMeta(request, id):
  resource = models.Resource.objects.get(pk=id)
  if request.method == 'POST':
    form = forms.MetadataForm(request.POST)
  else:
    form = forms.MetadataForm()
  if form.is_valid():
    meta,created = models.Metadata.objects.get_or_create(resource=resource,
        name=form.cleaned_data['name'], type=form.cleaned_data['type'])
    meta.value = form.cleaned_data['value']
    meta.save()
    messages.info(request, "Metadata saved.")
    return HttpResponseRedirect(reverse('spiff.inventory.views.view',
      kwargs={'id': resource.id}))
  return render_to_response('inventory/addMeta.html', {'item':resource,
    'metaForm': form},
      context_instance=RequestContext(request))

@permission_required('inventory.can_train')
def train(request, id):
  resource = models.Resource.objects.get(pk=id)
  training = None
  try:
    training = request.user.member.trainings.get(resource__id=id)
  except models.TrainingLevel.DoesNotExist:
    pass
  if request.method == 'POST':
    form = forms.TrainingForm(request.POST, instance=training)
  else:
    form = forms.TrainingForm(instance=training)
  if form.is_valid():
    if not training:
      training = models.TrainingLevel.objects.create(rank=form.cleaned_data['rank'],
          comments=form.cleaned_data['comments'], member=request.user.member,
          resource=resource)
    else:
      training.comments = form.cleaned_data['comments']
      training.rank = form.cleaned_data['rank']
      training.save()
      messages.info(request, "Training Updated")
      return HttpResponseRedirect(reverse('spiff.inventory.views.view',
        kwargs={'id': resource.id}))
  return render_to_response('inventory/train.html', {'item':resource,
    'trainingForm': form},
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
