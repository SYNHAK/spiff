from django.template import RequestContext
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
import stripe
from django.http import HttpResponseRedirect
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, render
from openid_provider.models import OpenID
from spiff.views import ObjectView
import models
import forms

class MemberView(ObjectView):
  model = models.Member
  template_name = 'membership/view.html'
  index_template_name = 'membership/index.html'
  slug_field = 'user__username'

  def get(self, request, *args, **kwargs):
    if request.user.has_perm('membership.list_members'):
      return super(MemberView, self).get(request, *args, **kwargs)
    raise PermissionDenied()

  def instances(self, request, *args, **kwargs):
    viewHidden = request.user.has_perm('membership.can_view_hidden_members')
    return models.Member.objects.filter(
      Q(user__is_active=True) |
      Q(user__groups__rank__isActiveMembership=True)).filter(
      Q(hidden=False) |
      Q(hidden=viewHidden)).distinct() 

  def instance(self, request, *args, **kwargs):
    viewHidden = request.user.has_perm('membership.can_view_hidden_members')
    return models.Member.objects.filter(
      Q(user__username=kwargs['user__username'])).filter(
      Q(user__is_active=True) |
      Q(user__groups__rank__isActiveMembership=True)).filter(
      Q(hidden=False) |
      Q(hidden=viewHidden)).distinct().get()

  def get_context_data(self, request, instance, instances, **kwargs):
    cxt = super(MemberView, self).get_context_data(
      request,
      instance,
      instances,
      **kwargs)
    if instance:
      openid,created = OpenID.objects.get_or_create(default=True, user=instance)
      cxt['openid'] = openid
    return cxt

def edit(request, username=None):
  if username is None:
    user = request.user
  else:
    user = User.objects.get(username=username)
  if user != request.user and not request.user.has_perm('auth.can_change_user'):
    raise PermissionDenied()
  fields = models.Field.objects.filter()
  values = user.member.attributes.all()
  if request.method == "POST":
    userForm = forms.UserForm(request.POST, instance=user)
    profileForm = forms.ProfileForm(request.POST, fields=fields, values=values)
  else:
    userForm = forms.UserForm(instance=user)
    profileForm = forms.ProfileForm(fields=fields, values=values)
  if userForm.is_valid() and profileForm.is_valid():
    user.first_name = userForm.cleaned_data['firstName']
    user.last_name = userForm.cleaned_data['lastName']
    user.email = userForm.cleaned_data['email']
    user.save()
    member = user.member
    member.tagline = userForm.cleaned_data['tagline']
    member.hidden = userForm.cleaned_data['hidden']
    member.save()
    for f in fields:
      value,created = models.FieldValue.objects.get_or_create(member=member, field=f)
      value.value = profileForm.fieldValue(f)
      value.save()
    messages.info(request, "Profile Saved.")

  return render_to_response('membership/edit.html',
      {'editUser': user, 'userForm':userForm, 'profileForm':profileForm},
      context_instance=RequestContext(request))

@permission_required('membership.can_change_member_rank')
def editRank(request, username):
  user = User.objects.get(username=username)
  if request.method == 'POST':
    rankForm = forms.RankForm(request.POST)
  else:
    rankForm = forms.RankForm(instance=user)
  if rankForm.is_valid():
    user.groups = rankForm.cleaned_data['groups']
    user.save()
    messages.info(request, "Ranks saved.")
    return HttpResponseRedirect(reverse('membership:view', kwargs={'user__username': user.username}))
  return render_to_response('membership/editRank.html',
      {'editUser': user, 'rankForm': rankForm},
      context_instance=RequestContext(request))
