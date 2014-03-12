import requests
import json
import logging
import datetime
import urlparse

log = logging.getLogger('spiff')

class Backend(object):
  def get(self, uri, verify, headers, params):
    raise NotImplemented

  def post(self, uri, verify, headers, data):
    raise NotImplemented

  def patch(self, uri, verify, headers, data):
    raise NotImplemented

  def delete(self, uri, verify, headers, data):
    raise NotImplemented

  def processResponse(self, response, status, blankResponse=False):
    raise NotImplemented

class RequestsBackend(Backend):
  def get(self, uri, verify, headers, params):
    return requests.get(uri, verify=verify, headers=headers, params=params)

  def post(self, uri, verify, headers, data):
    return requests.post(uri, data=data, verify=verify, headers=headers)

  def patch(self, uri, verify, headers, data):
    return requests.patch(uri, data=data, verify=verify, headers=headers)

  def delete(self, uri, verify, headers, params):
    return requests.delete(uri, params=params, verify=verify, headers=headers)

  def processResponse(self, response, status, blankResponse=False):
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
    if not blankResponse:
      return response.json()
    return None

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
  def __init__(self, uri, verify=True, backend=RequestsBackend()):
    super(API, self).__init__()
    self.__uri = urlparse.urlparse(uri)
    self.__token = None
    self.__verify = verify
    self.__backend = backend

  def __repr__(self):
    return "API(%r)"%(self.__uri.geturl())

  def __str__(self):
    return repr(self)

  def subUri(self, uri):
    if not uri.endswith('/'):
      uri += '/'
    if uri.startswith(self.__uri.path):
      return urlparse.urlunparse((self.__uri.scheme, self.__uri.netloc, uri, None,
        None, None))
    else:
      return urlparse.urljoin(self.__uri.geturl(), uri)
    raise ValueError

  def getRequestHeaders(self):
    headers = {
      'accept': 'application/json',
      'content-type': 'application/json'
    }

    if self.__token:
      headers['authorization'] = 'Bearer '+self.__token
    return headers

  def get(self, uri, status=200, **kwargs):
    return self.processResponse(self.getRaw(uri, **kwargs), status)

  def post(self, uri, status=201, **kwargs):
    return self.processResponse(self.postRaw(uri, kwargs), status)

  def patch(self, uri, status=202, **kwargs):
    return self.processResponse(self.patchRaw(uri, kwargs), status)

  def delete(self, uri, status=204, **kwargs):
    return self.processResponse(self.deleteRaw(uri, **kwargs), status,
        blankResponse=True)

  def deleteRaw(self, uri, **kwargs):
    uri = self.subUri(uri)
    log.debug("Requesting via DELETE %s: %r", uri, kwargs)
    return self.__backend.delete(uri, self.__verify,
        self.getRequestHeaders(), kwargs)

  def getRaw(self, uri, **kwargs):
    uri = self.subUri(uri)
    log.debug("Requesting via GET %s: %r", uri, kwargs)
    return self.__backend.get(uri, self.__verify,
        self.getRequestHeaders(), kwargs)

  def postRaw(self, uri, value):
    data = SpiffObjectEncoder(self, indent=2).encode(value)
    uri = self.subUri(uri)
    log.debug("Requesting via POST %s: %s", uri, data)
    return self.__backend.post(uri, self.__verify,
        self.getRequestHeaders(), data)

  def patchRaw(self, uri, value):
    data = SpiffObjectEncoder(self, indent=2).encode(value)
    uri = self.subUri(uri)
    log.debug("Requesting via PATCH %s: %s", uri, data)
    return self.__backend.patch(uri, self.__verify, self.getRequestHeaders(),
        data)

  def processResponse(self, response, status, blankResponse=False):
    return self.__backend.processResponse(response, status, blankResponse)

  def login(self, username, password):
    ret = self.post('v1/member/login/', username=username, password=password,
        status=200)
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
    return SpiffObject(self, self.post('v1/%s/'%(type), **kwargs))

class ObjectList(object):
  def __init__(self, api, type, filters={}):
    self.__api = api
    self.__type = type
    self.__cache = {}
    self.__count = 50
    self.__max = -1
    self.__filters = {}
    for name, value in filters.iteritems():
      if isinstance(value, SpiffObject):
        self.__filters[name] = value.id
      else:
        self.__filters[name] = value

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
    params['limit'] = count
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
      raise KeyError(offset)
    if offset not in self.__cache:
      self.__loadSlice(max(0, offset-5), 10)
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
    self.__saveData = {}
    assert(isinstance(self.__data, dict))
    if type is None:
      self.__type = self.__data['resource_uri'].split('/')[1]
    else:
      self.__type = type

  @property
  def type(self):
    return self.__type

  def save(self):
    if len(self.__saveData):
      self.__api.patch(self.resource_uri, **self.__saveData)
      for k,v in self.__saveData.iteritems():
        self.__data[k] = v
      self.__saveData = {}

  def delete(self):
    self.__api.delete(self.resource_uri)

  def refresh(self):
    self.__saveData = {}
    self.__data = self.__api.get(self.resource_uri)

  def __repr__(self):
    return "SpiffObject(%r, %r, %r)"%(self.__api, self.__data,
        self.__type)

  def __unicode__(self):
    return str(self)

  def __str__(self):
    return "%s(%r)"%(self.__type,
        SpiffObjectEncoder(self.__api, indent=4).encode(self.__data))

  def __getattr__(self, key):
    if key in self.__saveData:
      return self.__saveData[key]
    return self.__data[key]

  def __getitem__(self, key):
    if key in self.__saveData:
      return self.__saveData[key]
    return self.__data[key]

  def __setitem__(self, key, value):
    self.__saveData[key] = value

  def __setattr__(self, key, value):
    if key.startswith("_"):
      super(SpiffObject, self).__setattr__(key, value)
    else:
      self.__saveData[key] = value
