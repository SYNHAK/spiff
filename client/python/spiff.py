import requests

class API(object):
    def __init__(self, uri, verify=True):
        self.__uri = uri
        self.__verify = verify
        self.__db = {}
        self.__plurals = {}

    @property
    def uri(self):
        return self.__uri

    def clearCache(self):
        self.__db = {}

    def get(self, resource):
        return requests.get("%s/%s"%(self.__uri,resource), verify=self.__verify)

    def post(self, resource, value):
        return requests.post("%s/%s"%(self.__uri, resource), data=value, verify=self.__verify)

    def storeObject(self, obj):
        if obj.uriType not in self.__db:
            self.__db[obj.uriType] = {}
        self.__db[obj.uriType][obj.id] = obj
        self.__plurals[obj.type] = obj.uriType

    def _expand(self, data):
        ret = data
        if (isinstance(data, dict)):
          ret = {}
          for attr in data.iterkeys():
            ret[attr] = self._expand(data[attr])
          if '_type' in data:
            ret = ModelObject.new(self, ret)
        elif (isinstance(data, list)):
          ret = []
          for d in data:
            ret.append(self._expand(d))
        elif (isinstance(data, basestring) and data.startswith("#")):
          ret = ModelObject.new(self, data)
        return ret

    def objects(self, uriType):
        ret = []
        data = self.get("%s/.json"%(uriType)).json()
        return self._expand(data)

    def object(self, uriType, id, refresh=False):
        id = int(id)
        if uriType not in self.__db:
            self.__db[uriType] = {}
        if id in self.__db[uriType]:
            if refresh:
                del self.__db[uriType][id]
            else:
                return self.__db[uriType][id]

        res = self.get("%s/%s.json"%(uriType, id)).json()
        return ModelObject.new(self, res)

    def resolve(self, singularType, id):
        pluralType = self.__plurals[singularType]
        return self.object(pluralType, id)

    def resources(self):
        return self.objects("resources")

    def members(self):
        return self.objects("members")

    def sensors(self):
        return self.objects("sensors")

    def sensor(self, id):
        return self.object("sensors", id)

    def events(self):
        return self.objects("events")

class ModelObject(dict):
    def __init__(self, api, data):
        super(dict, self).__init__()
        assert(data is not None)
        self.__data = data
        self.__api = api
        if isinstance(self.__data, dict):
            self.__api.storeObject(self)

    @property
    def api(self):
        return self.__api

    @property
    def id(self):
        return self.resolve()['id']

    @property
    def type(self):
        return self.resolve()['_type']

    @property
    def uriType(self):
        return self.resolve()['_plural_type']

    def qrCode(self, size=10):
        return requests.get("%s%s/%s/qr-%s.png"%(self.__api.uri, 'resources', self.id, size), verify=False).content

    def refresh(self):
        if isinstance(self.__data, dict):
            self.__data = self.api.object(self.uriType, self.id, refresh=True).__data
        else:
            self.resolve().refresh()

    def resolve(self):
        if isinstance(self.__data, dict):
            return self.__data
        tokens = self.__data.split("#")
        return self.__api.resolve(tokens[1], tokens[2]).resolve()

    def keys(self):
        ret = []
        for k in self.resolve().iterkeys():
            ret.append(k)
        return ret

    def __getitem__(self, key):
        return self.resolve()[key]

    @staticmethod
    def new(api, data):
        cls = ModelObject
        if isinstance(data, dict):
            if data['_type'] == "resource":
                cls = Resource
            elif data['_type'] == "sensor":
                cls = Sensor
        return cls(api, data)

class Sensor(ModelObject):
    def setValue(self, value):
        ret = self.api.post("sensors/%d.json"%(self.id), {'data': value})
        self.refresh()
        return ret

    @property
    def value(self):
        return self.resolve()['value']

class Resource(ModelObject):
    def meta(self, name):
        for m in self['metadata']:
            if m['name'] == name:
                return m
        return None
