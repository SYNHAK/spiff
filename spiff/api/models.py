from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from south.signals import post_migrate
from django.db.models.signals import post_syncdb
from spiff.api.plugins import find_api_classes
from tastypie.resources import ModelResource
from spiff.api import SpiffAuthorization
from spiff import funcLog

def add_resource_permissions(*args, **kwargs):
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
      if len(conditions) == 0:
        conditions = (None,)

      for condition in conditions:
        for operation in operations:
          # build our permission slug
          if condition:
            codename = "%s_%s_%s" % (operation[0], condition[0], content_type.model)
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
                                      name=name[:49])
            funcLog().debug("Created permission %s.%s (%s)", content_type.app_label, codename, name)

# check for all our view permissions after a syncdb
post_migrate.connect(add_resource_permissions)
post_syncdb.connect(add_resource_permissions)
