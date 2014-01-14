from django.conf.urls import url
from tastypie import fields
from tastypie.authorization import DjangoAuthorization
from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash
import models

class TrainingResource(ModelResource):
  member = fields.ToOneField('spiff.membership.v1_api.MemberResource', 'member', full=True)
  resource = fields.ToOneField('spiff.inventory.v1_api.ResourceResource', 'resource')
  rank = fields.CharField('comment', blank=True)

  class Meta:
    authorization = DjangoAuthorization()
    queryset = models.Certification.objects.all()

class ResourceMetadataResource(ModelResource):
  name = fields.CharField('name')
  value = fields.CharField('value')
  resource = fields.ToOneField('spiff.inventory.v1_api.ResourceResource', 'resource')

  class Meta:
    authorization = DjangoAuthorization()
    queryset = models.Metadata.objects.all()

  def obj_create(self, bundle, **kwargs):
    bundle = super(ResourceMetadataResource, self).obj_create(
      bundle, **kwargs)
    bundle.obj.resource.logChange(
      member=bundle.request.user.member,
      property=bundle.obj.name,
      new=bundle.obj.value)
    return bundle

  def obj_update(self, bundle, **kwargs):
    oldVal = bundle.obj.value
    oldName = bundle.obj.name
    bundle = super(ResourceMetadataResource, self).obj_update(
      bundle, **kwargs)
    bundle.obj.resource.logChange(
      member=bundle.request.user.member,
      property=bundle.obj.name,
      new=bundle.obj.value,
      old=oldVal)
    return bundle

  def obj_delete(self, bundle, **kwargs):
    if bundle.request.user.is_anonymous():
      raise ImmediateHttpResponse(response=HttpUnauthorized());
    oldMeta = models.Metadata.objects.get(pk=kwargs['pk'])
    oldName = oldMeta.name
    oldValue = oldMeta.value
    oldMember = bundle.request.user.member
    bundle = super(ResourceMetadataResource, self).obj_delete(
      bundle, **kwargs)
    oldMeta.resource.logChange(
      member=oldMember,
      property=oldName,
      old=oldValue,
      new=None)
    return bundle

class ChangelogResource(ModelResource):
  member = fields.ToOneField('spiff.membership.v1_api.MemberResource', 'member')
  old = fields.CharField('old', null=True)
  new = fields.CharField('new', null=True)
  property = fields.CharField('property', null=True)
  stamp = fields.DateTimeField('stamp')

  class Meta:
    queryset = models.Change.objects.all()

class ResourceResource(ModelResource):
  name = fields.CharField('name')
  metadata = fields.ToManyField(ResourceMetadataResource, 'metadata', full=True)

  class Meta:
    queryset = models.Resource.objects.all()
    resource_name = 'resource'

  def prepend_urls(self):
    return [
      url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/changelog%s$" %
        (self._meta.resource_name, trailing_slash()),
        self.wrap_view('get_changelog'), name="api_get_changelog"),
      url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/metadata%s$" %
        (self._meta.resource_name, trailing_slash()),
        self.wrap_view('get_metadata'), name="api_get_metadata"),
      url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/training%s$" %
        (self._meta.resource_name, trailing_slash()),
        self.wrap_view('get_training'), name="api_get_training"),
    ]

  def get_training(self, request, **kwargs):
    try:
      bundle = self.build_bundle(data={'pk': kwargs['pk']}, request=request)
      obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
    except ObjectDoesNotExist:
      return HttpGone()

    return TrainingResource().get_list(request, resource_id=obj.pk)

  def get_metadata(self, request, **kwargs):
    try:
      bundle = self.build_bundle(data={'pk': kwargs['pk']}, request=request)
      obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
    except ObjectDoesNotExist:
      return HttpGone()

    return ResourceMetadataResource().get_list(request, resource_id=obj.pk)

  def get_changelog(self, request, **kwargs):
    try:
      bundle = self.build_bundle(data={'pk': kwargs['pk']}, request=request)
      obj = self.cached_obj_get(bundle=bundle, **self.remove_api_resource_names(kwargs))
    except ObjectDoesNotExist:
      return HttpGone()

    return ChangelogResource().get_list(request, resource_id=obj.pk)

