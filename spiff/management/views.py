from django.contrib.auth.decorators import permission_required
import string
import random
from django.contrib.auth.models import User
from django.contrib import messages
from django.template import RequestContext
from django.shortcuts import render_to_response
from spiff.membership.forms import ProfileForm
from spiff.management.forms import RegistrationForm, UserSelectionForm
from spiff.membership.models import Field, FieldValue
from spiff.notification_loader import notification

def index(request):
  if request.user.is_staff:
    return render_to_response('management/index.html',
      context_instance=RequestContext(request))

@permission_required('payment.add_invoice')
def billUser(request, username=None):
  user = None
  invoice = None

  if request.method == 'POST':
    form = UserSelectionForm(request.POST)
  else:
    form = UserSelectionForm()
  if form.is_valid():
    user = form.cleaned_data['user']
  if username is not None:
    user = User.objects.get(username=username)
  if user:
    invoice = user.member.generateMonthlyInvoice()
    if invoice:
      messages.info(request, 'Invoice generated.')
    else:
      messages.info(request, 'User already has invoice for this month.')
  return render_to_response('management/billUser.html',
    {'form': form, 'invoice': invoice},
    context_instance=RequestContext(request))

@permission_required('auth.add_user')
def createUser(request):
  fields = Field.objects.filter(required=True)
  if request.method == 'POST':
    userForm = RegistrationForm(request.POST, prefix='user')
    profileForm = ProfileForm(request.POST, fields=fields, prefix='profile')
  else:
    userForm = RegistrationForm(prefix='user')
    profileForm = ProfileForm(fields=fields, prefix='profile')
  if userForm.is_valid() and profileForm.is_valid():
    randomPassword = ''.join([random.choice(string.letters+string.punctuation+string.digits) for i in range(15)])
    if userForm.cleaned_data['username'] == '':
      userForm.cleaned_data['username'] = userForm.cleaned_data['email'].split('@')[0]
    oldUser = None
    try:
      oldUser = User.objects.get(username__exact=userForm.cleaned_data['username'])
    except User.DoesNotExist:
      pass
    if oldUser:
      messages.info(request, "The username '%s' already exists."%(userForm.cleaned_data['username']))
    else:
      user = User.objects.create_user(
        userForm.cleaned_data['username'],
        userForm.cleaned_data['email'],
        randomPassword
      )
      user.first_name = userForm.cleaned_data['firstName']
      user.last_name = userForm.cleaned_data['lastName']
      user.save()
      member = user.member
      member.tagline = userForm.cleaned_data['tagline']
      member.save()
      messages.info(request, "User '%s' created!"%userForm.cleaned_data['username'])
      notification.send(
        [user],
        "account_created",
        {'user': user, 'creator': request.user}
      )
      for field in fields:
        FieldValue.objects.create(field=field,
            value=profileForm.fieldValue(field), member=member)
  return render_to_response('management/createUser.html',
    {'userForm': userForm, 'profileForm':
      profileForm},
    context_instance=RequestContext(request))
