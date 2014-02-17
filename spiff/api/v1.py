from tastypie.api import Api
from spiff.api.plugins import find_api_classes
from tastypie.resources import Resource

v1_api = Api(api_name='v1')
for api in find_api_classes('v1_api', Resource, lambda x:hasattr(x, 'Meta')):
  v1_api.register(api())

