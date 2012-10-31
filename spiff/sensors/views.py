from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
import models

def index(request):
  sensors = models.Sensor.objects.all()
  return render_to_response('sensors/index.html',
      {'sensors': sensors},
      context_instance=RequestContext(request))

@csrf_exempt
def view(request, id):
  sensor = models.Sensor.objects.get(pk=id)
  if request.POST:
    models.SensorValue.objects.create(sensor=sensor,
        value=request.POST['data'])
  return render_to_response('sensors/view.html',
      {'sensor': sensor},
      context_instance=RequestContext(request))
