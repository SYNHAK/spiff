from django.shortcuts import render_to_response
from django.template import RequestContext
from spiff.views import ObjectView
import models

def index(request):
  sensors = models.Sensor.objects.all()
  return render_to_response('sensors/index.html',
      {'sensors': sensors},
      context_instance=RequestContext(request))

class SensorView(ObjectView):
  model = models.Sensor
  template_name = 'sensors/view.html'
  index_template_name = 'sensors/index.html'

  def post(self, request, instance, *args, **kwargs):
    """
    Updates the sensor's value.
    """
    models.SensorValue.objects.create(
        sensor=instance,
        value=request.POST['data'])
    return super(SensorView, self).post(request, instance, *args, **kwargs)
