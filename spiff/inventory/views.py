from django.template import RequestContext
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.sites.models import get_current_site
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_control
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import permission_required
from spiff.views import ObjectView
from cStringIO import StringIO
import models
import qrcode
import forms

def view(request, id):
  resource = models.Resource.objects.get(pk=id)
  training = None
  if not request.user.is_anonymous():
    try:
      training = request.user.member.trainings.get(resource=resource)
    except models.TrainingLevel.DoesNotExist:
      pass
  return render_to_response('inventory/view.html', {'item':resource, 'myTraining': training},
      context_instance=RequestContext(request))

class InventoryView(ObjectView):
  model = models.Resource
  template_name = 'inventory/view.html'
  index_template_name = 'inventory/index.html'

  def get_context_data(self, request, instance, instances, **kwargs):
    cxt = super(InventoryView, self).get_context_data(request, instance,
        instances, **kwargs)
    if instance:
      cxt['myTraining'] = None
      if not request.user.is_anonymous():
        try:
          cxt['myTraining'] = request.user.member.trainings.get(resource=instance)
        except models.TrainingLevel.DoesNotExist:
          pass
    return cxt

@permission_required('inventory.can_change_metadata')
def addMeta(request, id):
  resource = models.Resource.objects.get(pk=id)
  if request.method == 'POST':
    form = forms.MetadataForm(request.POST)
  else:
    form = forms.MetadataForm()
  if form.is_valid():
    meta,created = models.Metadata.objects.get_or_create(resource=resource,
        name=form.cleaned_data['name'], type=form.cleaned_data['type'])
    if created:
      oldValue = None
    else:
      oldValue = meta.value
    meta.value = form.cleaned_data['value']
    meta.save()
    messages.info(request, "Metadata saved.")
    resource.logChange(
        member=request.user.member,
        old=oldValue,
        new=meta.value,
        property=meta.name)

    return HttpResponseRedirect(reverse('inventory:view',
      kwargs={'id': resource.id}))
  return render_to_response('inventory/addMeta.html', {'item':resource,
    'metaForm': form},
      context_instance=RequestContext(request))

@permission_required('inventory.can_train')
def promoteTraining(request, id):
  training = models.TrainingLevel.objects.get(id=id)
  resource = training.resource
  myTraining = request.user.member.trainings.get(resource=resource)
  if myTraining == training:
    raise PermissionDenied()
  oldValue = training.rank
  training.rank = myTraining.rank + 1
  training.save()
  messages.info(request, "Promoted!")
  resource.logChange(
      member=request.user.member,
      old=oldValue,
      new=training.rank,
      trained_member=training.member)
  return HttpResponseRedirect(reverse('inventory:view', 
    kwargs={'id': resource.id}))

@permission_required('inventory.can_train')
def train(request, id):
  resource = models.Resource.objects.get(pk=id)
  training = None
  try:
    training = request.user.member.trainings.get(resource__id=id)
  except models.TrainingLevel.DoesNotExist:
    training = models.TrainingLevel.objects.create(member=request.user.member,
        resource=resource, rank=0)
    resource.logChange(
        member=request.user.member,
        new=training.rank,
        trained_member=training.member)
  messages.info(request, "Duly Noted.")
  return HttpResponseRedirect(reverse('inventory:view',
    kwargs={'id': resource.id}))

@cache_control(public=True, private=False, no_cache=False, no_transform=False, must_revalidate=False, proxy_revalidate=False, max_age=86400)
def qrCode(request, id):
  site = get_current_site(request)
  base = "%s://%s"%(request.META['wsgi.url_scheme'], site.domain)
  if request.META['SERVER_PORT'] != '80':
    base = "%s:%s"%(base, request.META['SERVER_PORT'])
  img = qrcode.make("%s%s"%(base,
    reverse('inventory:view', kwargs={'id': id})))
  buf = StringIO()
  img.save(buf, "PNG")
  return HttpResponse(buf.getvalue(), content_type="image/png")
