from django.conf import settings
from django.conf.urls import patterns, include
from tastypie.api import Api
from tastypie.resources import Resource, ModelResource
import importlib
import inspect
from south.signals import post_migrate
from django.db.models.signals import post_syncdb
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from tastypie.authorization import DjangoAuthorization
from spiff.api.plugins import find_api_classes
from spiff import funcLog

def add_resource_permissions(sender, **kwargs):
  """
  This syncdb hooks takes care of adding a view permission too all our 
  content types.
  """
  # for each of our content types
  for resource in find_api_classes('v1_api', ModelResource):
    auth = resource._meta.authorization
    content_type = ContentType.objects.get_for_model(resource._meta.queryset.model)
    if isinstance(auth, SpiffAuthorization):
      conditions = auth.conditions()
      operations = auth.operations()
      content_types = []
      if len(conditions) == 0:
        conditions = (None,)

      for condition in conditions:
        for operation in operations:
          # build our permission slug
          if condition:
            codename = "%s_%s_%s" % (operation[0], content_type.model,
                condition[0])
            name = "Can %s %s, when %s" % (operation[1], content_type.name,
                condition[1])
          else:
            codename = "%s_%s" % (operation[1], content_type.model)
            name = "Can %s %s" % (operation[1], content_type.name)

          # if it doesn't exist..
          if not Permission.objects.filter(content_type=content_type, codename=codename):
            # add it
            Permission.objects.create(content_type=content_type,
                                      codename=codename,
                                      name=name)
            funcLog().debug("Created permission %s.%s (%s)", content_type.app_label, codename, name)

# check for all our view permissions after a syncdb
post_migrate.connect(add_resource_permissions)
post_syncdb.connect(add_resource_permissions)

class SpiffAuthorization(DjangoAuthorization):

  def conditions(self):
    return (
      None,
    )

  def operations(self):
    return (
      ('list', 'list'),
      ('view', 'view'),
      ('change', 'change'),
      ('delete', 'delete'),
      ('add', 'add'),
    )

  def check_perm(self, request, model, name, op):
    klass = self.base_checks(request, model.__class__)
    permName = '%s.%s_%s' % (model.__class__._meta.app_label, name,
        model.__class__._meta.module_name)
    ret = request.user.has_perm(permName)
    funcLog().debug("%r", request.user.user_permissions.all())
    funcLog().debug("Checking %s for %s: %s", request.user, permName, ret)
    return ret

  def check_list(self, object_list, bundle, op, perm=None):
    func = getattr(super(SpiffAuthorization, self), '%s_list'%(op))
    permitted = func(object_list, bundle)
    ret = []
    if perm is not None:
      for obj in permitted:
        if self.check_perm(bundle.request, obj, perm, op):
          ret.append(obj)
    return ret

  def check_detail(self, object_list, bundle, op, perm=None):
    func = getattr(super(SpiffAuthorization, self), '%s_detail'%(op))
    if func(object_list, bundle):
      if perm is not None:
        return self.check_perm(bundle.request, bundle.obj, perm, op)
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

  @classmethod
  def conditions():
    return (
      ('others', 'owned by other users'),
    )+super(OwnedObjectAuthorization, self).conditions()

  def check_perm(self, request, model, name, op):
    if getattr(model, self._attr) != request.user:
      return super(OwnedObjectAuthorization, self).check_perm(request,
          model.__class__, '%s_others'%(name), op)
    return super(OwnedObjectAuthorization, self).check_perm(request,
        model.__class__, name, op)

v1_api = Api(api_name='v1')
for api in find_api_classes('v1_api', Resource, lambda x:hasattr(x, 'Meta')):
  v1_api.register(api())
