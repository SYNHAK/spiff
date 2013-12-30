from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

urlpatterns = patterns('ui',
    url(r'^(?P<name>.+)$', 'views.partial', name='partial'),
    url(r'^', TemplateView.as_view(template_name='index.html'), name='index')
)
