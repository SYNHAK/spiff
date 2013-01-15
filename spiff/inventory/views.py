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
def deleteMeta(request, id):
  meta = models.Metadata.objects.get(pk=id)
  resource = meta.resource
  oldValue = meta.value
  resource.logChange(
      member=request.user.member,
      old=meta.value,
      new=None,
      property=meta.name)
  meta.delete()
  messages.info(request, "Metadata removed.")
  return HttpResponseRedirect(reverse('inventory:view',
    kwargs={'id': resource.id}))

@permission_required('inventory.can_change_metadata')
def addMeta(request, id, name=None):
  """
  Allows you to add/modify metadata on a resource.
  """
  resource = models.Resource.objects.get(pk=id)
  if request.method == 'POST':
    form = forms.MetadataForm(request.POST, initial={'name': name})
  else:
    try:
      oldMeta = models.Metadata.objects.get(resource=resource, name=name)
      form = forms.MetadataForm(instance=oldMeta)
    except models.Metadata.DoesNotExist:
      form = forms.MetadataForm(initial={'name': name})
  if form.is_valid():
    try:
      meta = models.Metadata.objects.get(
        resource=resource,
        name = form.cleaned_data['name']
      )
      created = False
    except models.Metadata.DoesNotExist:
      meta = models.Metadata.objects.create(resource=resource,
          name=form.cleaned_data['name'], type=form.cleaned_data['type'])
      created = True
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
  """
  Promotes another user in the training system.
  """
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
  """
  Adds the current user to the training list for a resource.
  """
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
def qrCode(request, id, size=10):
  site = get_current_site(request)
  base = "%s://%s"%(request.META['wsgi.url_scheme'], site.domain)
  if (request.META['wsgi.url_scheme'] == 'http' and request.META['SERVER_PORT'] != '80') or (request.META['wsgi.url_scheme'] == 'https' and request.META['SERVER_PORT'] != '443'):
    base = "%s:%s"%(base, request.META['SERVER_PORT'])
  img = qrcode.make("%s%s"%(base,
    reverse('inventory:view', kwargs={'id': id})),
    box_size=size,
    border=0
  )
  buf = StringIO()
  img.save(buf, "PNG")
  return HttpResponse(buf.getvalue(), content_type="image/png")


@permission_required('inventory.add_resource')
def addResource(request):
  if request.method == 'POST':
    form = forms.AddResourceForm(request.POST)
  else:
    form = forms.AddResourceForm()
  if form.is_valid():
    res = models.Resource.objects.create(
      name=form.cleaned_data['name'],
      trainable=form.cleaned_data['trainable']
    )
    res.logChange(
      member = request.user.member,
    )
    messages.info(request, "Resource created.")
    return HttpResponseRedirect(
      reverse(
        'inventory:view',
        kwargs={'id': res.id}
      )
    )
  return render_to_response(
    'inventory/addResource.html', 
    {
      'form': form
    },
    context_instance=RequestContext(request)
  )
