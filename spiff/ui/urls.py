from django.conf.urls import patterns, include, url

urlpatterns = patterns('ui',
    url(r'^(?P<name>.+)$', 'views.partial', name='partial'),
    url(r'^', 'views.index', name='index')
)
