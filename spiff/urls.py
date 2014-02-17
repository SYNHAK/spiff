from django.conf.urls import patterns, include, url
from spiff.api.v1 import v1_api
from django.views.generic import RedirectView
from django.templatetags.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^status.json$', 'spiff.api.views.spaceapi'),
    url(r'^$', RedirectView.as_view(url=static('index.html')), name='root'),
    url(r'^', include(v1_api.urls)),

    #$url(r'^events/', include('spiff.events.urls', namespace='events')),
    #$url(r'^openid_provider/', include('openid_provider.urls')),
    #$url(r'^openid/untrust/(?P<id>.*)', 'spiff.local.views.untrust_openid_root'),
    #$url(r'^openid/unassociate/(?P<id>.*)', 'spiff.local.views.unassociate_openid'),
    #$url(r'^openid/', include('django_openid_auth.urls')),

    #$# Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    #$url(r'^register$', 'spiff.local.views.register'),
    #$url(r'^search$', 'spiff.local.views.search'),
    #$#url(r'^webfinger/', include('webfinger.urls')),
)
