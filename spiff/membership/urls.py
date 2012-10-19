from django.conf.urls import patterns, include, url

urlpatterns = patterns('spiff.membership',
  url(r'^$', 'views.index'),
)
