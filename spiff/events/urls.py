from django.conf.urls import patterns, include, url

urlpatterns = patterns('spiff.events',
  url(r'^$', 'views.index'),
  url(r'^(?P<id>[0-9]+)$', 'views.view'),
  url(r'^create$', 'views.create'),
  url(r'^(?P<id>[0-9]+)/attach$', 'views.addResource'),
  url(r'^(?P<id>[0-9]+)/attend$', 'views.attend'),
)
