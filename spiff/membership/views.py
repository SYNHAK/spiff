from django.template import RequestContext
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from openid_provider.models import OpenID
from spiff.views import ObjectView
import models
import forms

class MemberView(ObjectView):
  model = models.Member
  template_name = 'membership/view.html'
  index_template_name = 'membership/index.html'
  slug_field = 'user__username'

  def instances(self, request, *args, **kwargs):
    return User.objects.filter(
      Q(is_active=True) |
      Q(groups__rank__isActiveMembership=True)).distinct()

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
    member.birthday = userForm.cleaned_data['birthday']
    member.profession = userForm.cleaned_data['profession']
    member.save()
    for f in fields:
      value,created = models.FieldValue.objects.get_or_create(member=member, field=f)
      value.value = profileForm.fieldValue(f)
      value.save()
    messages.info(request, "Profile Saved.")

  return render_to_response('membership/edit.html',
      {'editUser': user, 'userForm':userForm, 'profileForm':profileForm},
      context_instance=RequestContext(request))
