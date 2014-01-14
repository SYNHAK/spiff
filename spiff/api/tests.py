from django.test import TestCase
from django.test.client import Client
from spiff import membership, inventory, sensors, local
from django.contrib.auth.models import User, Permission
import json
import functools

def withPermission(perm):
  def wrapIt(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
      self.grantPermission(perm)
      return func(self, *args, **kwargs)
    return wrapper
  return wrapIt

def withLogin(func):
  @functools.wraps(func)
  def wrapper(self, *args, **kwargs):
    self.login()
    return func(self, *args, **kwargs)
  return wrapper

class ClientTestMixin(TestCase):
  def setupClient(self):
    self.client = Client()

class APITestMixin(ClientTestMixin):
  def setupAPI(self):
    self.user = User.objects.create_user('test', 'test@example.com', 'test')
    self.user.first_name = 'Test'
    self.user.last_name = 'McTesterson'
    self.user.save()
    self.setupClient()

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
    value = sensors.models.SensorValue.objects.create(
      sensor=sensor,
      value="true"
    )
    data = self.getAPI()
    self.assertTrue(data['open'])
    value = sensors.models.SensorValue.objects.create(
      sensor=sensor,
      value="false"
    )
    data = self.getAPI()
    self.assertFalse(data['open'])
