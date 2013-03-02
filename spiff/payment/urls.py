from django.conf.urls import patterns, include, url

urlpatterns = patterns('spiff.payment',
  url(r'^pay/(?P<invoiceID>.+)$', 'views.pay', name='pay'),
  url(r'^invoice/(?P<invoiceID>.+)$', 'views.viewInvoice', name='viewInvoice'),
)
