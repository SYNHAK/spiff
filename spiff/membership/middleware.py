from django.conf import settings
from django.contrib.auth.models import User
import models

if not hasattr(settings, 'ANONYMOUS_USER_ID'):
  settings.ANONYMOUS_USER_ID = 0

class AnonymousUser(User):
  class Meta:
    proxy = True

class AnonymousUserMiddleware(object):
  def process_request(self, request):
    if request.user.is_anonymous():
      if settings.ANONYMOUS_USER_ID == 0:
        request.user, created = AnonymousUser.objects.get_or_create(
          username='anonymous',
          email='anonymous@example.com',
          password=''
        )
        if created:
          request.user.set_unusable_password()
          request.user.save()
      else:
        request.user = User.objects.get(settings.ANONYMOUS_USER_ID)
    try:
      member = request.user.member
    except models.Member.DoesNotExist:
      request.user.member, created = models.Member.objects.get_or_create(user=request.user)
      request.user.save()
    return None
