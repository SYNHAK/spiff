import models

class AnonymousUserMiddleware(object):
  def process_request(self, request):
    if request.user.is_anonymous():
      request.user = models.get_anonymous_user()
    return None
