from django.test import TestCase
from django.test.client import Client
from spiff import membership, inventory
from django.contrib.auth.models import User
import json

class APITestMixin(TestCase):
  def setupAPI(self):
    self.user = User.objects.create_user('test', 'test@example.com', 'test')
    self.user.first_name = 'Test'
    self.user.last_name = 'McTesterson'
    self.user.save()
    self.client = Client()

  def login(self):
    self.client.login(username='test', password='test')

  def postAPIRaw(self, endpoint, struct=None):
    if struct:
      return self.client.post(
        endpoint,
        json.dumps(struct),
        content_type="application/json"
      )
    else:
      return self.client.post(endpoint)

  def getAPIRaw(self, endpoint, args=None):
    if args:
      return self.client.get(endpoint, args)
    return self.client.get(endpoint)

  def postAPI(self, endpoint, struct=None, status=200):
    ret = self.postAPIRaw(endpoint, struct)
    self.assertEqual(ret.status_code, status)
    if len(ret.content):
      ret = json.loads(ret.content)
      self.assertIn('objects', ret)
    else:
      ret = None
    return ret

  def getAPI(self, endpoint, struct=None, status=200):
    ret = self.getAPIRaw(endpoint, struct)
    self.assertEqual(ret.status_code, status)
    ret = json.loads(ret.content)
    self.assertIn('objects', ret)
    return ret

class ResourceTestMixin(TestCase):
  def setupResource(self, name='Resource'):
    resource = inventory.models.Resource.objects.create(
      name='Resource',
      trainable=True,
    )
    if not hasattr(self, 'resource'):
      self.resource = resource
    return resource

class ResourceMetadataTest(APITestMixin, ResourceTestMixin):
  def setUp(self):
    self.setupAPI()
    self.setupResource()

  def addMeta(self, resource, name, value, type=inventory.models.META_TYPES[0][0]):
    meta = inventory.models.Metadata.objects.create(
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

  def testCreateMeta(self):
    meta = self.getMeta()
    self.assertEqual(len(meta['objects']), 0)

    self.login()

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

class MemberTest(APITestMixin):
  def setUp(self):
    self.setupAPI()

  def search(self, status=200, **kwargs):
    return self.getAPI('/v1/member/search/', kwargs, status=status)

  def testLogin(self):
    response = self.postAPIRaw('/v1/member/login/', {'username': 'test', 'password': 'test'})
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.cookies.has_key('sessionid'))

  def testBadLogin(self):
    response = self.postAPIRaw('/v1/member/login/', {'username': 'test',
      'password': 'nottest'})
    self.assertEqual(response.status_code, 401)
    self.assertFalse(response.cookies.has_key('sessionid'))

  def testDisabledLogin(self):
    self.user.is_active = False
    self.user.save()
    response = self.postAPIRaw('/v1/member/login/', {'username': 'test',
      'password': 'test'})
    self.assertEqual(response.status_code, 403)
    self.assertFalse(response.cookies.has_key('sessionid'))

  def testLogout(self):
    response = self.postAPIRaw('/v1/member/login/', {'username': 'test', 'password': 'test'})
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.cookies.has_key('sessionid'))
    session = response.cookies.get('sessionid')
    response = self.getAPIRaw('/v1/member/logout/')
    self.assertTrue(response.cookies.has_key('sessionid'))
    self.assertNotEqual(session, response.cookies.has_key('sessionid'))

  def testSearchFullname(self):
    ret = self.search(fullName='Test McTesterson')
    self.assertIn('objects', ret)
    self.assertEqual(len(ret['objects']), 1)

  def testSearchPartialFirst(self):
    ret = self.search(fullName='Test')
    self.assertIn('objects', ret)
    self.assertEqual(len(ret['objects']), 1)

  def testSearchPartialLast(self):
    ret = self.search(fullName='McTesterson')
    self.assertEqual(len(ret['objects']), 1)

  def testSearchPartialMultiple(self):
    guesterson = User.objects.create_user('guest', 'guest@example.com', 'guest')
    guesterson.first_name = 'Guest'
    guesterson.last_name = 'McGuesterson'
    guesterson.save()

    ret = self.search(fullName='esterson')
    self.assertIn('objects', ret)
    self.assertEqual(len(ret['objects']), 2)
