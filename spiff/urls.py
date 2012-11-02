from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'spiff.local.views.index', name='home'),
    url(r'^accounts/profile/$', 'spiff.local.views.index'),
    url(r'^members/', include('spiff.membership.urls')),
    url(r'^sensors/', include('spiff.sensors.urls', namespace='sensors')),
    url(r'^resources/', include('spiff.inventory.urls', namespace='inventory')),
    url(r'^events/', include('spiff.events.urls')),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^openid_provider/', include('openid_provider.urls')),
    url(r'^openid/untrust/(?P<id>.*)', 'spiff.local.views.untrust_openid_root'),
    url(r'^openid/unassociate/(?P<id>.*)', 'spiff.local.views.unassociate_openid'),
    url(r'^openid/', include('django_openid_auth.urls')),
    # Examples:
    # url(r'^$', 'spiff.views.home', name='home'),
    # url(r'^spiff/', include('spiff.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^register$', 'spiff.local.views.register'),
    url(r'^search$', 'spiff.local.views.search'),
    url(r'^status.json$', 'spiff.local.views.spaceapi'),
    url(r'^webfinger/', include('webfinger.urls')),

    url(r'^', include('wellknown.urls')),
)
