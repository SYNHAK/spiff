from django.conf.urls import patterns, include, url

urlpatterns = patterns('spiff.sensors',
    url(r'^$', 'views.index'),
    url(r'^(?P<id>[0-9]+)$', 'views.view'),
)
