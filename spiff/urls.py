from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'spiff.local.views.index', name='home'),
    # Examples:
    # url(r'^$', 'spiff.views.home', name='home'),
    # url(r'^spiff/', include('spiff.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^logout', 'django.contrib.auth.views.logout'),
)
