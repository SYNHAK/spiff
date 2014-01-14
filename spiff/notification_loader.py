from django.conf import settings
notification = None
if "notification" in settings.INSTALLED_APPS:
  from notification import models as notification
