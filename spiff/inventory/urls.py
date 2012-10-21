from django.conf.urls import patterns, include, url

urlpatterns = patterns('spiff.inventory',
  url(r'^$', 'views.index'),
  url(r'^(?P<id>[0-9]+)$', 'views.view'),
  url(r'^(?P<id>[0-9]+)/qr$', 'views.qrCode'),
  url(r'^(?P<id>[0-9]+)/add$', 'views.addMeta'),
  url(r'^(?P<id>[0-9]+)/train$', 'views.train'),
)
