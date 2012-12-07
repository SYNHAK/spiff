from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns('spiff.membership',
  url(r'^edit/(?P<username>.+)$', 'views.edit', name='edit'),
  url(r'^edit$', 'views.edit', name='edit'),
)

urlpatterns += views.MemberView.as_url()
