import requests
import json
from tastypie_client import Api

class API(Api):
  def __init__(self, uri, verify=True):
    super(API, self).__init__(uri+'v1/')
    self.__uri = uri
    self.__token = None
    self.__verify = verify

  def subUri(self, uri):
    return '/'.join((self.__uri, uri))

  def get(self, uri, **kwargs):
    headers = {
      'accept': 'application/json',
      'content-type': 'application/json'
    }
    if self.__token:
      headers['authorization'] = 'Bearer '+self.__token
    return requests.get(
      self.subUri(uri),
      verify=self.__verify,
      headers=headers,
      params=kwargs
    )

  def post(self, uri, value):
    data = json.dumps(value)
    headers = {
      'accept': 'application/json',
      'content-type': 'application/json'
    }

    if self.__token:
      headers['authorization'] = 'Bearer '+self.__token
    return requests.post(
      self.subUri(uri),
      data=data,
      verify=self.__verify,
      headers=headers
    )

  def login(self, username, password):
    data={'username': username, 'password': password}
    ret = self.post('v1/member/login/', data).json()
    if 'token' in ret:
      self.__token = ret['token']
      return True
    return False

  @property
  def uri(self):
    return self.__uri

  def getList(self, type, **kwargs):
    return ObjectList(self, type, kwargs)

  def resources(self, **kwargs):
    return self.getList('resource', **kwargs)

class ObjectList(object):
  def __init__(self, api, type, filters={}):
    self.__api = api
    self.__type = type
    self.__cache = {}
    self.__count = 20
    self.__max = -1
    self.__filters = filters

    self.__loadSlice(0)

  def __len__(self):
    if self.__max == -1:
      self.__loadSlice(0)
    return self.__max

  def __loadSlice(self, offset, count=None):
    if count is None:
      count = self.__count
    params = {}
    params.update(self.__filters)
    params['offset'] = offset
    params['count'] = count
    data = self.__api.get('/'.join(('v1', self.__type)), **params).json()
    self.__max = data['meta']['total_count']
    for i in range(0, len(data['objects'])):
      self.__cache[i+offset] = data['objects'][i]

  def __getitem__(self, offset):
    if self.__max >= 0 and offset >= self.__max:
      raise KeyError
    if offset not in self.__cache:
      self.__loadSlice(offset)
    return self.__cache[offset]

  def __iter__(self):
    return ObjectListIter(self)

class ObjectListIter(object):
  def __init__(self, objectList):
    self.__list = objectList
    self.__pos = -1

  def __iter__(self):
    return self

  def next(self):
    self.__pos += 1
    if self.__pos >= len(self.__list):
      raise StopIteration
    return self.__list[self.__pos]

class SpiffObject(object):
  def __init__(self, api, type, data):
    self.__api = api
    self.__type = type
    self.__data = data

  def update(self, **kwargs):
    for k,v in kwargs.iteritems():
      self.__data[k] = v
    self.__api.post('/'.join(('v1', self.__type)), kwargs)
