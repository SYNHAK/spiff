import models

class AnonymousUserMiddleware(object):
  def process_request(self, request):
    if request.user.is_anonymous():
      request.user = models.get_anonymous_user()
    else:
      request.user = models.AuthenticatedUser.objects.get(pk=request.user.pk)
    return None
