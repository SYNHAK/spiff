from django.conf import settings
from django.conf.urls import patterns, include
from tastypie.api import Api
from tastypie.resources import Resource
import importlib
import inspect
from south.signals import post_migrate
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

v1_api = Api(api_name='v1')
for app in map(lambda x:'%s.v1_api'%(x), settings.INSTALLED_APPS):
  try:
    appAPI = importlib.import_module(app)
  except ImportError:
    continue
  for name, cls in inspect.getmembers(appAPI):
    if inspect.isclass(cls) and issubclass(cls, Resource) and hasattr(cls, 'Meta'):
      v1_api.register(cls())

def add_view_permissions(sender, **kwargs):
  """
  This syncdb hooks takes care of adding a view permission too all our 
  content types.
  """
  # for each of our content types
  for content_type in ContentType.objects.all():
    for action in ['view', 'list']:
      # build our permission slug
      codename = "%s_%s" % (action, content_type.model)

      # if it doesn't exist..
      if not Permission.objects.filter(content_type=content_type, codename=codename):
        # add it
        Permission.objects.create(content_type=content_type,
                                  codename=codename,
                                  name="Can %s %s" % (action, content_type.name))

# check for all our view permissions after a syncdb
post_migrate.connect(add_view_permissions)
