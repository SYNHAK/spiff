from django.conf import settings
import importlib
import inspect

def find_api_classes(*args, **kwargs):
  for app, cls in find_api_implementations(*args, **kwargs):
    yield cls

def find_api_implementations(module, superclass, test=lambda x: True):
  for app in map(lambda x:'%s.%s'%(x, module), settings.INSTALLED_APPS):
    try:
      appAPI = importlib.import_module(app)
    except ImportError:
      continue
    for name, cls in inspect.getmembers(appAPI):
      if inspect.isclass(cls) and issubclass(cls, superclass) and not cls is superclass and test(cls):
        yield (app, cls)
