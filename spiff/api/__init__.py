from tastypie.authorization import Authorization
from spiff import funcLog

class SpiffAuthorization(Authorization):

  def conditions(self):
    return (
      None,
    )

  def operations(self):
    return (
      ('create', 'create'),
      ('read', 'read'),
      ('update', 'update'),
      ('delete', 'delete'),
    )

  def base_checks(self, request, model_klass):
    if not model_klass or not getattr(model_klass, '_meta', None):
      return False

    if not hasattr(request, 'user'):
      return False

    return model_klass

  def check_perm(self, bundle, model, permName):
    permName = '%s.%s_%s' % (model.__class__._meta.app_label, permName,
        model.__class__._meta.module_name)
    ret = bundle.request.user.has_perm(permName)
    funcLog().debug("Checking %s for %s: %s", bundle.request.user, permName, ret)
    return ret

  def check_list(self, object_list, bundle, op):
    ret = []
    for obj in object_list:
      if self.check_perm(bundle, obj, op):
        ret.append(obj)
    return ret

  def check_detail(self, object_list, bundle, op):
    return self.check_perm(bundle, bundle.obj, op)

  def read_list(self, object_list, bundle):
    return self.check_list(object_list, bundle, 'read')

  def read_detail(self, object_list, bundle):
    return self.check_detail(object_list, bundle, 'read')

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

  def conditions(self):
    return (
      ('others', 'owned by other users'),
      ('own', 'owned by self'),
    )+super(OwnedObjectAuthorization, self).conditions()

  def check_perm(self, bundle, model, name):
    u = getattr(model, self._attr)
    funcLog().info("Checking %r for ownership of %r (%r)", bundle.request.user, model, u)
    if u.pk == bundle.request.user.pk:
      return super(OwnedObjectAuthorization, self).check_perm(bundle,
          model, '%s_own'%(name))
    return super(OwnedObjectAuthorization, self).check_perm(bundle,
        model, '%s_others'%(name))
