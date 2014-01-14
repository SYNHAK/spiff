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
import forms

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

@permission_required('inventory.certify')
def uncertify(request, certID):
  """
  Deletes a certification
  """
  cert = models.Certification.objects.get(pk=certID)
  resource = cert.resource
  oldValue = cert.comment
  oldMember = cert.member
  cert.delete()
  resource.logChange(
    member = request.user.member,
    old=oldValue,
    new=None,
    trained_member=oldMember
  )
  messages.info(request, "Certification removed.")
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
