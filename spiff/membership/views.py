from django.template import RequestContext
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
import models
import forms

def index(request):
  users = User.objects.filter(Q(is_active=True) |
      Q(groups__rank__isActiveMembership=True)).distinct()
  return render_to_response('membership/index.html',
      {'users': users},
      context_instance=RequestContext(request))

def view(request, username):
  user = User.objects.get(username=username)
  return render_to_response('membership/view.html',
      {'viewUser': user},
      context_instance=RequestContext(request))

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
