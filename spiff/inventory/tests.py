"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from spiff.api.tests import APITestMixin, withPermission, withLogin 
import models

class ResourceTestMixin(TestCase):
  def setupResource(self, name='Resource'):
    resource = models.Resource.objects.create(
      name='Resource',
      trainable=True,
    )
    if not hasattr(self, 'resource'):
      self.resource = resource
    return resource

class ResourceMetadataAPITest(APITestMixin, ResourceTestMixin):
  def setUp(self):
    self.setupAPI()
    self.setupResource()

  def addMeta(self, resource, name, value, type=models.META_TYPES[0][0]):
    meta = models.Metadata.objects.create(
      resource=resource,
      name=name,
      value=value,
      type=type
    )
    return meta

  def getMeta(self, resource=None):
    if resource is None:
      resource = self.resource
    return self.getAPI('/v1/resource/%s/metadata/'%(resource.id))

  def testGetBlankMeta(self):
    meta = self.getMeta()
    self.assertTrue(len(meta['objects']) == 0)

  def testGetSingleMeta(self):
    self.addMeta(self.resource, 'meta-test', 'meta-test-value')
    meta = self.getMeta()
    self.assertEqual(len(meta['objects']),  1)
    self.assertEqual(meta['objects'][0]['name'], 'meta-test')
    self.assertEqual(meta['objects'][0]['value'], 'meta-test-value')

  def testUnauthedCreateMeta(self):
    self.postAPI('/v1/metadata/',{
      'resource': '/v1/resource/%s/'%(self.resource.id),
      'name': 'api-meta',
      'value': 'api-meta-test',
      'type': 0
    }, status=401)

  @withLogin
  def testUnpermissionedCreateMeta(self):
    meta = self.getMeta()
    self.assertEqual(len(meta['objects']), 0)

    self.postAPI('/v1/metadata/',{
      'resource': '/v1/resource/%s/'%(self.resource.id),
      'name': 'api-meta',
      'value': 'api-meta-test',
      'type': 0
    }, status=401)

  @withLogin
  @withPermission('inventory.add_metadata')
  def testCreateMeta(self):
    meta = self.getMeta()
    self.assertEqual(len(meta['objects']), 0)

    self.postAPI('/v1/metadata/',{
      'resource': '/v1/resource/%s/'%(self.resource.id),
      'name': 'api-meta',
      'value': 'api-meta-test',
      'type': 0
    }, status=201)

    meta = self.getMeta()
    self.assertEqual(len(meta['objects']), 1)
    self.assertEqual(meta['objects'][0]['name'], 'api-meta')
    self.assertEqual(meta['objects'][0]['value'], 'api-meta-test')
