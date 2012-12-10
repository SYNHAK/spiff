from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns('spiff.membership',
  url(r'^edit/(?P<username>.+)$', 'views.edit', name='edit'),
  url(r'^edit$', 'views.edit', name='edit'),
  url(r'^editRank/(?P<username>.+)$', 'views.editRank', name='editRank'),
  url(r'^addPayment/(?P<username>.+)$', 'views.addPayment', name='addPayment'),
  url(r'^pay$', 'views.pay', name='pay'),
)

urlpatterns += views.MemberView.as_url()
