from django.conf.urls import patterns, include, url

urlpatterns = patterns('spiff.management',
  url(r'^$', 'views.index', name='index'),
)

