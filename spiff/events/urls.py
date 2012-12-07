from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns('spiff.events',
  url(r'^create$', 'views.create', name='create'),
  url(r'^(?P<id>[0-9]+)/attach$', 'views.addResource', name='addResource'),
  url(r'^(?P<id>[0-9]+)/attend$', 'views.attend', name='attend'),
)

urlpatterns += views.EventView.as_url()
