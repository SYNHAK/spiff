from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns('spiff.sensors',
)

urlpatterns += views.SensorView.as_url()
