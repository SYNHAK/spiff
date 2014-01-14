from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns('spiff.inventory',
  url(r'^add$', 'views.addResource', name='add'),
  url(r'^(?P<id>[0-9]+)/qr.png$', 'views.qrCode', name='qr'),
  url(r'^(?P<id>[0-9]+)/qr-(?P<size>[0-9]+).png$', 'views.qrCode', name='qr'),
  url(r'^(?P<id>[0-9]+)/train$', 'views.train', name='train'),
  url(r'^(?P<certID>[0-9]+)/uncertify$', 'views.uncertify', name='uncertify'),
  url(r'^(?P<id>[0-9]+)/promote$', 'views.promoteTraining', name='promote'),
)
