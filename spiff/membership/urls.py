from django.conf.urls import patterns, include, url

urlpatterns = patterns('spiff.membership',
  url(r'^$', 'views.index'),
  url(r'^view/(?P<username>.+)$', 'views.view'),
  url(r'^edit/(?P<username>.+)$', 'views.edit'),
  url(r'^edit$', 'views.edit'),
)
