from django.conf import settings
from django.conf.urls import patterns, include
from tastypie.api import Api
from tastypie.resources import Resource
import importlib
import inspect
from south.signals import post_migrate
from django.db.models.signals import post_syncdb
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
post_syncdb.connect(add_view_permissions)

class SpiffAuthorization(DjangoAuthorization):
  def check_perm(self, request, model, name):
    klass = self.base_checks(request, model.__class__)
    permName = '%s.%s_%s' % (model.__class__._meta.app_label, name,
        model.__class__._meta.module_name)
    return request.user.has_perm(permName)

  def check_list(self, object_list, bundle, op, perm=None):
    func = getattr(super(SpiffAuthorization, self), '%s_list'%(op))
    permitted = func(object_list, bundle)
    ret = []
    if perm is not None:
      for obj in permitted:
        if self.check_perm(bundle.request, obj, perm):
          ret.append(obj)
    return ret

  def check_detail(self, object_list, bundle, op, perm=None):
    func = getattr(super(SpiffAuthorization, self), '%s_detail'%(op))
    if func(object_list, bundle):
      if perm is not None:
        return self.check_perm(bundle.request, bundle.obj, perm)
      return True
    return False

  def read_list(self, object_list, bundle):
    return self.check_list(object_list, bundle, 'read', 'list')

  def read_detail(self, object_list, bundle):
    return self.check_detail(object_list, bundle, 'read', 'view')

  def create_list(self, object_list, bundle):
    return self.check_list(object_list, bundle, 'create')

  def create_detail(self, object_list, bundle):
    return self.check_detail(object_list, bundle, 'create')

  def update_list(self, object_list, bundle):
    return self.check_list(object_list, bundle, 'update')

  def update_detail(self, object_list, bundle):
    return self.check_detail(object_list, bundle, 'update')

  def delete_list(self, object_list, bundle):
    return self.check_list(object_list, bundle, 'delete')

  def delete_detail(self, object_list, bundle):
    return self.check_detail(object_list, bundle, 'delete')

class OwnedObjectAuthorization(SpiffAuthorization):
  def __init__(self, attrName):
    self._attr = attrName

  def check_perm(self, request, model, name):
    if getattr(model, self._attr) != request.user:
      return super(OwnedObjectAuthorization, self).check_perm(request,
          model.__class__, '%s_others'%(name))
    return super(OwnedObjectAuthorization, self).check_perm(request,
        model.__class__, name)

v1_api = Api(api_name='v1')
for api in find_api_classes('v1_api', Resource, lambda x:hasattr(x, 'Meta')):
  v1_api.register(api())
