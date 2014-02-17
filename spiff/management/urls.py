from django.conf.urls import patterns, url

urlpatterns = patterns('spiff.management',
  url(r'^$', 'views.index', name='index'),
  url(r'^createUser$', 'views.createUser', name='createUser'),
  url(r'^billUser$', 'views.billUser', name='billUser'),
)

