import requests

class API(object):
    def __init__(self, uri, verify=True):
        self.__uri = uri
        self.__verify = verify
        self.__db = {}

    @property
    def uri(self):
        return self.__uri

    def get(self, resource):
        return requests.get("%s/%s"%(self.__uri,resource), verify=self.__verify)

    def post(self, resource, value):
        return requests.post("%s/%s"%(self.__uri, resource), data=value, verify=self.__verify)

    def object(self, klass, id):
        if klass not in self.__db:
            self.__db[klass] = {}
        return self.__db[klass][id]

    def storeObject(self, klass, id, obj):
        if klass not in self.__db:
            self.__db[klass] = {}
        self.__db[klass][id] = obj

    def objects(self, uriType):
        ret = []
        for res in self.get("%s/.json"%(uriType)).json:
            obj = ModelObject.new(self, res)
            ret.append(obj)
        return ret

    def object(self, uriType, id):
        res = self.get("%s/%s.json"%(uriType, id)).json
        return ModelObject.new(self, res)

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
            self.__api.storeObject(self.__data['_type'], self.__data['id'], self)

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
        return requests.get("%s%s/%s/qr-%s.png"%(self.__api.uri, 'resources', self.__data['id'], size), verify=False).content

    def refresh(self):
        if isinstance(self.__data, dict):
            self.__data = self.api.object(self.uriType, self.id).__data
        else:
            self.resolve().refresh()

    def resolve(self):
        if isinstance(self.__data, dict):
            return self.__data
        print "Resolving", self, self.__data
        tokens = self.__data.split("#")
        return self.__api.object(tokens[1], tokens[2]).resolve()

    def keys(self):
        ret = []
        for k in self.resolve().iterkeys():
            ret.append(k)
        return ret

    def __getitem__(self, key):
        val = self.resolve()[key]
        if isinstance(val, str):
            tokens = val.split("#")
            if len(tokens) == 3:
                return self.__api.object(tokens[1], tokens[2])
        return val

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
