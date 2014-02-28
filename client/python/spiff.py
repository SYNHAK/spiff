import requests
import json
import logging
import datetime

log = logging.getLogger('spiff')

class ServerError(Exception):
  def __init__(self, message):
    super(ServerError, self).__init__()
    self.__msg = message

  def __str__(self):
    return self.__msg

  def __repr__(self):
    return "ServerError(%r)"%(self.__msg)

class SpiffObjectEncoder(json.JSONEncoder):
  def __init__(self, api, *args, **kwargs):
    super(SpiffObjectEncoder, self).__init__(*args, **kwargs)
    self.__api = api

  def default(self, obj):
    if isinstance(obj, SpiffObject):
      return obj.resource_uri
    if isinstance(obj, datetime.date):
      return str(obj)
    if isinstance(obj, ObjectList):
      l = []
      for o in obj:
        l.append(o.resource_uri)
      return self.default(l)
    try:
      iterable = iter(obj)
    except TypeError:
      pass
    else:
      return list(iterable)
    return super(SpiffObjectEncoder, self).default(obj)

class API(object):
  def __init__(self, uri, verify=True):
    super(API, self).__init__()
    self.__uri = uri
    self.__token = None
    self.__verify = verify

  def __repr__(self):
    return "API(%r)"%(self.__uri)

  def __str__(self):
    return repr(self)

  def subUri(self, uri):
    return '/'.join((self.__uri, uri))

  def getRequestHeaders(self):
    headers = {
      'accept': 'application/json',
      'content-type': 'application/json'
    }

    if self.__token:
      headers['authorization'] = 'Bearer '+self.__token
    return headers

  def getRaw(self, uri, **kwargs):
    log.debug("Requesting via GET %s: %r", uri, kwargs)
    if uri[0] == '/':
      uri = uri[1:]
    return requests.get(
      self.subUri(uri),
      verify=self.__verify,
      headers=self.getRequestHeaders(),
      params=kwargs
    )

  def postRaw(self, uri, value):
    data = SpiffObjectEncoder(self, indent=2).encode(value)
    log.debug("Requesting via POST %s: %s", uri, data)
    return requests.post(
      self.subUri(uri),
      data=data,
      verify=self.__verify,
      headers=self.getRequestHeaders()
    )

  def get(self, uri, status=200, **kwargs):
    return self.processResponse(self.getRaw(uri, **kwargs), status)

  def post(self, uri, status=201, **kwargs):
    return self.processResponse(self.postRaw(uri, kwargs), status)

  def patch(self, uri, status=200, **kwargs):
    return self.processResponse(self.patchRaw(uri, kwargs), status)

  def patchRaw(self, uri, value):
    data = SpiffObjectEncoder(self, indent=2).encode(value)
    log.debug("Requesting via PATCH %s: %s", uri, data)
    return requests.patch(
      self.subUri(uri),
      data=data,
      verify=self.__verify,
      headers=self.getRequestHeaders()
    )

  def processResponse(self, response, status):
    if response.status_code != status:
      if len(response.content):
        try:
          errorMsg = response.json()
        except ValueError:
          raise ServerError(response.content)
        if 'traceback' in errorMsg:
          raise ServerError(errorMsg['traceback'])
        else:
          raise ServerError(str(errorMsg['error']))
      else:
        response.raise_for_status()
    return response.json()

  def login(self, username, password):
    ret = self.post('v1/member/login/', username=username, password=password)
    if 'token' in ret:
      self.__token = ret['token']
      return True
    return False

  @property
  def uri(self):
    return self.__uri

  def getOne(self, type, id=None):
    if id is None:
      if isinstance(type, SpiffObject):
        return SpiffObject(self, self.get(type.resource_uri))
      else:
        return SpiffObject(self, self.get(type))
    return SpiffObject(self, self.get('%s/%s'%(type, id)))

  def getList(self, type, **kwargs):
    return ObjectList(self, type, kwargs)

  def create(self, type, **kwargs):
    return self.post('v1/%s/'%(type), **kwargs)

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
    data = self.__api.get('/'.join(('v1', self.__type)), **params)
    self.__max = data['meta']['total_count']
    for i in range(0, len(data['objects'])):
      self.__cache[i+offset] = SpiffObject(self.__api,
          data['objects'][i])

  def __getitem__(self, offset):
    if isinstance(offset, slice):
      ret = []
      step = offset.step
      if step is None:
        step = 1
      for i in range(offset.start, offset.stop, step):
        ret.append(self[i])
      return ret
    if self.__max >= 0 and offset >= self.__max:
      raise KeyError
    if offset not in self.__cache:
      self.__loadSlice(offset)
    return self.__cache[offset]

  def __iter__(self):
    return ObjectListIter(self)

  def __str__(self):
    return repr(self)

  def __repr__(self):
    total = len(self)
    if total >= 5:
      return repr(self[0:3]+['...'])
    return repr(self[0:len(self)])

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
  def __init__(self, api, data, type=None):
    self.__api = api
    self.__data = data
    assert(isinstance(self.__data, dict))
    if type is None:
      self.__type = self.__data['resource_uri'].split('/')[1]
    else:
      self.__type = type

  @property
  def type(self):
    return self.__type

  def update(self, **kwargs):
    for k,v in kwargs.iteritems():
      self.__data[k] = v
    self.__api.post('/'.join(('v1', self.__type)), kwargs)

  def __repr__(self):
    return "SpiffObject(%r, %r, %r)"%(self.__api, self.__data,
        self.__type)

  def __unicode__(self):
    return str(self)

  def __str__(self):
    return "%s(%r)"%(self.__type,
        SpiffObjectEncoder(self.__api, indent=4).encode(self.__data))

  def __getattr__(self, name):
    return self.__data[name]

  def __getitem__(self, key):
    return self.__data[key]
