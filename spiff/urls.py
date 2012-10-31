from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'spiff.local.views.index', name='home'),
    url(r'^members/', include('spiff.membership.urls')),
    url(r'^sensors/', include('spiff.sensors.urls')),
    url(r'^resources/', include('spiff.inventory.urls')),
    url(r'^events/', include('spiff.events.urls')),
    url(r'^accounts/profile/$', 'spiff.local.views.index', name='home'),
    # Examples:
    # url(r'^$', 'spiff.views.home', name='home'),
    # url(r'^spiff/', include('spiff.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^logout$', 'django.contrib.auth.views.logout', {'next_page':'/'}),
    url(r'^login$', 'django.contrib.auth.views.login'),
    url(r'^register$', 'spiff.local.views.register'),
    url(r'^search$', 'spiff.local.views.search'),
)
