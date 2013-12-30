from django.conf.urls import patterns, include
from resources import *
from tastypie.api import Api

v1_api = Api(api_name='v1')
v1_api.register(MemberResource())
v1_api.register(RankResource())
v1_api.register(GroupResource())
v1_api.register(InvoiceResource())
v1_api.register(LineItemResource())
v1_api.register(PaymentResource())
