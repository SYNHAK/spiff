from django.conf.urls import patterns, include, url

urlpatterns = patterns('spiff.payment',
  url(r'^pay/(?P<invoiceID>.+)$', 'views.pay', name='pay'),
  url(r'^addPayment/(?P<invoiceID>.+)$', 'views.addPayment', name='addPayment'),
  url(r'^invoice/(?P<invoiceID>.+)$', 'views.viewInvoice', name='viewInvoice'),
)
