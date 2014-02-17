from django.conf.urls import patterns
import views

urlpatterns = patterns('spiff.sensors',
)

urlpatterns += views.SensorView.as_url()
