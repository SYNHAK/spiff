from django.test import TestCase
from django.test.client import Client
from spiff import membership, sensors, local, funcLog
from django.contrib.auth.models import User, Permission, Group
import json
import functools

def withAdmin(func):
  @functools.wraps(func)
  def wrapper(self, *args, **kwargs):
    self.user.is_superuser = True
    self.user.save()
    return func(self, *args, **kwargs)
  return wrapper

def withoutPermission(perm):
  def wrapIt(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
      self.revokePermission(perm)
      return func(self, *args, **kwargs)
    return wrapper
  return wrapIt

def withPermission(perm):
  def wrapIt(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
      self.grantPermission(perm)
      return func(self, *args, **kwargs)
    return wrapper
  return wrapIt

def withUser(username='test', password='test'):
  def wrap(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
      self.user = self.createUser(username, password)
      self.password = password
      return func(self, *args, **kwargs)
    return wrapper
  if callable(username):
    f = username
    username = 'test'
    return wrap(f)
  return wrap

def withLogin(func):
  @functools.wraps(func)
  @withUser
  def wrapper(self, *args, **kwargs):
    self.login()
    return func(self, *args, **kwargs)
  return wrapper


class ClientTestMixin(TestCase):
  def setupClient(self):
    self.client = Client()

class APITestMixin(ClientTestMixin):
  def setupAPI(self):
    self.user = membership.models.get_anonymous_user()
    self.setupClient()

  def revokePermission(self, permissionName):
    funcLog().info("Revoking %s from %s", permissionName, self.user)
    appName, name = permissionName.split('.', 1)
    perm = Permission.objects.get(
      codename=name,
      content_type__app_label=appName,
    )
    self.user.user_permissions.remove(perm)
    self.user.save()
    return perm

  def grantPermission(self, permissionName):
    funcLog().info("Granting %s to %s", permissionName, self.user)
    appName, name = permissionName.split('.', 1)
    perm = Permission.objects.get(
      codename=name,
      content_type__app_label=appName,
    )
    self.user.user_permissions.add(perm)
    self.user.save()
    return perm

  def createUser(self, username, password):
    funcLog().info("Creating user %s with password %s", username, password)
    user = User.objects.create_user(username, 'test@example.com', password)
    user.first_name = 'Test'
    user.last_name = 'McTesterson'
    user.save()
    return user

  def createGroup(self, name):
    funcLog().info("Creating group %s", name)
    group = Group.objects.create(name=name)
    return group

  def login(self):
    funcLog().info("Logging in with test user")
    self.client.login(username=self.user.username, password=self.password)

  def deleteAPIRaw(self, endpoint, struct=None):
    if struct:
      funcLog().info("Deleting %s: %r", endpoint, struct)
      return self.client.delete(
        endpoint,
        json.dumps(struct),
        content_type="application/json"
      )
    else:
      funcLog().info("Deleting %s", endpoint)
      return self.client.delete(endpoint)

  def postAPIRaw(self, endpoint, struct=None):
    if struct:
      funcLog().info("Posting to %s: %r", endpoint, struct)
      return self.client.post(
        endpoint,
        json.dumps(struct),
        content_type="application/json"
      )
    else:
      funcLog().info("Posting to %s", endpoint)
      return self.client.post(endpoint)

  def getAPIRaw(self, endpoint, args=None):
    if args:
      funcLog().info("Requesting %s with %r", endpoint, args)
      return self.client.get(endpoint, args)
    funcLog().info("Requesting %s", endpoint)
    return self.client.get(endpoint)
  
  def patchAPIRaw(self, endpoint, struct=None):
    if struct:
      funcLog().info("Patching %s with %r", endpoint, struct)
      return self.client.patch(
        endpoint,
        json.dumps(struct),
        content_type = 'application/json'
      )
    funcLog().info("Patching %s", endpoint)
    return self.client.patch(endpoint)

  def deleteAPI(self, endpoint, struct=None, status=204):
    ret = self.deleteAPIRaw(endpoint, struct)
    self.assertEqual(ret.status_code, status)
    if len(ret.content):
      ret = json.loads(ret.content)
    else:
      ret = None
    return ret

  def patchAPI(self, endpoint, struct=None, status=202):
    ret = self.patchAPIRaw(endpoint, struct)
    self.assertEqual(ret.status_code, status)
    if len(ret.content):
      ret = json.loads(ret.content)
    else:
      ret = None
    return ret

  def postAPI(self, endpoint, struct=None, status=201):
    ret = self.postAPIRaw(endpoint, struct)
    funcLog().debug("Got result %s: %s", ret.status_code, ret.content)
    self.assertEqual(ret.status_code, status)
    if len(ret.content):
      ret = json.loads(ret.content)
    else:
      ret = None
    return ret

  def getAPI(self, endpoint, struct=None, status=200):
    ret = self.getAPIRaw(endpoint, struct)
    self.assertEqual(ret.status_code, status)
    ret = json.loads(ret.content)
    return ret

class SpaceAPITest(ClientTestMixin):
  def setUp(self):
    self.setupClient()

  def getAPI(self):
    response = self.client.get('/status.json')
    self.assertEqual(response.status_code, 200)
    return json.loads(response.content)

  def testAPIStatus(self):
    response = self.client.get('/status.json')
    self.assertEqual(response.status_code, 200)

  def testMissingDoorSensorSensor(self):
    data = self.getAPI()
    self.assertFalse(data['open'])

  def testDoorSensor(self):
    conf = local.models.SpaceConfig.objects.all()[0]
    sensor = sensors.models.Sensor.objects.create(
      name='door',
      description='Door Test Sensor',
      type=sensors.models.SENSOR_TYPE_BOOLEAN,
    )
    conf.openSensor = sensor
    conf.save()
    sensors.models.SensorValue.objects.create(
      sensor=sensor,
      value="true"
    )
    data = self.getAPI()
    self.assertTrue(data['open'])
    sensors.models.SensorValue.objects.create(
      sensor=sensor,
      value="false"
    )
    data = self.getAPI()
    self.assertFalse(data['open'])
