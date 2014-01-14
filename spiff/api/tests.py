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

  def grantPermission(self, permissionName):
    appName, name = permissionName.split('.', 1)
    perm = Permission.objects.get(
      codename=name,
      content_type__app_label=appName,
    )
    self.user.user_permissions.add(perm)
    self.user.save()
    return perm

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

