from django.conf import settings
if "notification" in settings.INSTALLED_APPS:
  from notification import models as notification
else:
  notification = None
