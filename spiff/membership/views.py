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
    member.tagline = userForm.cleaned_data['tagline']
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

@permission_required('membership.can_add_due_payment')
def addPayment(request, username):
  user = User.objects.get(username=username)
  if request.method == 'POST':
    dueForm = forms.DueForm(request.POST)
  else:
    dueForm = forms.DueForm()
  if dueForm.is_valid():
    args = dueForm.cleaned_data
    args['user'] = request.user
    args['member'] = user.member
    payment = models.DuePayment.objects.create(**args)
    messages.info(request, "Payment added.")
    return HttpResponseRedirect(reverse('membership:view', kwargs={'user__username': user.username}))
  return render_to_response('membership/addDues.html',
      {'editUser': user, 'dueForm': dueForm},
      context_instance=RequestContext(request))

def pay(request):
  if request.method == 'POST':
    form = forms.PaymentForm(request.POST)
  else:
    form = forms.PaymentForm()
  rank = request.user.member.highestRank
  balance = request.user.member.outstandingDues
  if balance < 0.5:
    messages.error(request, "Your outstanding balance of $%d costs less than "
        "$0.50, which is too small for Stripe to process."%(balance))
    return render_to_response('membership/pay.html',
      {'form': form},
      context_instance=RequestContext(request))

  if form.is_valid():
    stripe.api_key = settings.STRIPE_KEY
    cardData = {}
    cardData['number'] = form.cleaned_data['card']
    cardData['exp_month'] = form.cleaned_data['month']
    cardData['exp_year'] = form.cleaned_data['year']
    cardData['cvc'] = form.cleaned_data['cvc']
    try:
      charge = stripe.Charge.create(
        amount = int(balance*100),
        currency = 'usd',
        card = cardData,
        description = 'Due payment from %s for %s'%(request.user.member.fullName, rank.group.name)
      )
      payment = models.DuePayment.objects.create(
        member = request.user.member,
        user = request.user,
        value = balance,
        status = models.DuePayment.STATUS_PAID,
        transactionID = charge.id,
        rank = rank,
        method = models.DuePayment.METHOD_STRIPE
      )
      messages.info(request, "Your payment has been processed. Thanks!")
      return HttpResponseRedirect(reverse('home'))
    except stripe.CardError, e:
      messages.error(request, "There was an error while processing your card: %s"%(e.message))
  return render_to_response('membership/pay.html',
      {'form': form},
      context_instance=RequestContext(request))
