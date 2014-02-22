import models
import jwt
from django.conf import settings

class JWTAuthMiddleware(object):
  def process_request(self, request):
    if 'HTTP_AUTHORIZATION' in request.META:
      token = request.META['HTTP_AUTHORIZATION'].split()
      if token[0] == 'Bearer':
        try:
          decoded = jwt.decode(token[1], settings.SECRET_KEY)
          request.user = models.AuthenticatedUser.objects.get(pk=decoded['id'])
        except jwt.DecodeError:
          pass
    if not hasattr(request, 'user'):
      request.user = models.get_anonymous_user()

class AnonymousUserMiddleware(object):
  def process_request(self, request):
    if request.user.is_anonymous():
      request.user = models.get_anonymous_user()
    else:
      request.user = models.AuthenticatedUser.objects.get(pk=request.user.pk)
    return None
