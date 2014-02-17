from django.conf.urls import patterns, url
import views

urlpatterns = patterns('spiff.events',
  url(r'^create$', 'views.create', name='create'),
  url(r'^(?P<id>[0-9]+)/attach$', 'views.addResource', name='addResource'),
  url(r'^(?P<id>[0-9]+)/edit$', 'views.edit', name='edit'),
  url(r'^(?P<id>[0-9]+)/attend$', 'views.attend', name='attend'),
  url(r'^(?P<id>[0-9]+)/addOrganizer$', 'views.addOrganizer', name='addOrganizer'),
  url(r'^(?P<id>[0-9]+)/removeOrganizer/(?P<userID>[0-9]+)$', 'views.removeOrganizer', name='removeOrganizer'),
)

urlpatterns += views.EventView.as_url()
