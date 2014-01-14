from django.conf import settings
from django.conf.urls import patterns, include
from tastypie.api import Api
from tastypie.resources import Resource
import importlib
import inspect

v1_api = Api(api_name='v1')
for app in map(lambda x:'%s.v1_api'%(x), settings.INSTALLED_APPS):
  try:
    appAPI = importlib.import_module(app)
  except ImportError:
    continue
  for name, cls in inspect.getmembers(appAPI):
    if inspect.isclass(cls) and issubclass(cls, Resource) and hasattr(cls, 'Meta'):
      v1_api.register(cls())
