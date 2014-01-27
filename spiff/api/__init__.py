from django.conf import settings
from django.conf.urls import patterns, include
from tastypie.api import Api
from tastypie.resources import Resource
import importlib
import inspect
from south.signals import post_migrate
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from tastypie.authorization import DjangoAuthorization
from spiff.api.plugins import find_api_classes

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

class SpiffAuthorization(DjangoAuthorization):
  def read_list(self, object_list, bundle):
    ret = super(SpiffAuthorization, self).read_list(object_list, bundle)
    klass = self.base_checks(bundle.request, object_list.model)
    permName = '%s.list_%s' % (klass._meta.app_label, klass._meta.module_name)
    if not bundle.request.user.has_perm(permName):
      return []
    return ret

  def read_detail(self, object_list, bundle):
    if super(SpiffAuthorization, self).read_detail(object_list, bundle):
      klass = self.base_checks(bundle.request, bundle.obj.__class__)
      permName = '%s.view_%s' % (klass._meta.app_label, klass._meta.module_name)
      return bundle.request.user.has_perm(permName)
    return False

v1_api = Api(api_name='v1')
for api in find_api_classes('v1_api', Resource, lambda x:hasattr(x, 'Meta')):
  v1_api.register(api())
