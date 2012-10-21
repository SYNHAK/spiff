from django.template import RequestContext
from django.shortcuts import render_to_response
import forms
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def index(request):
  if request.user.is_anonymous():
    return render_to_response('local/index_anonymous.html',
        context_instance=RequestContext(request))
  else:
    return render_to_response('local/index.html',
        context_instance=RequestContext(request))

def register(request):
  if request.method == 'POST':
    userForm = forms.UserForm(request.POST, prefix='user')
    memberForm = forms.MemberForm(request.POST, prefix='profile')
  else:
    userForm = forms.UserForm(prefix='user')
    memberForm = forms.MemberForm(prefix='profile')
  if userForm.is_valid() and memberForm.is_valid():
    oldUser = None
    try:
      oldUser = User.objects.get(username__exact=userForm.cleaned_data['username'])
    except ObjectDoesNotExist, e:
      pass
    if not oldUser:
      user = User.objects.create_user(userForm.cleaned_data['username'],
          userForm.cleaned_data['email'], userForm.cleaned_data['password'])
      user.first_name = memberForm.cleaned_data['firstName']
      user.last_name = memberForm.cleaned_data['lastName']
      user.save()
      member = user.member
      member.birthday = memberForm.cleaned_data['birthday']
      member.save()
      user = authenticate(username=userForm.cleaned_data['username'], password=userForm.cleaned_data['password'])
      login(request, user)
      messages.info(request, "Welcome!")
      return HttpResponseRedirect(reverse('home'))
  return render_to_response('local/register.html',
      {'userForm': userForm, 'memberForm': memberForm},
      context_instance=RequestContext(request))
