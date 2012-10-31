from django.views.generic import TemplateView
from copy import copy
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpResponse
from django.core import serializers
from django.db.models import Model, Manager
from django.db.models.query import QuerySet
import datetime

class ModelEncoder(json.JSONEncoder):
  def __init__(self, *args, **kwargs):
    super(ModelEncoder, self).__init__(*args, **kwargs)
    self._seen = []

  def default(self, o):
    if isinstance(o, Model):
      if o in self._seen:
        return "#%s#%s"%(o._meta.object_name, o.pk)
      self._seen.append(o)
      data = {}
      if hasattr(o, 'serialize'):
        return o.serialize()
      for f in o._meta.get_all_field_names():
        try:
          data[f] = getattr(o, f)
        except AttributeError:
          pass
      return data
    if isinstance(o, QuerySet):
      ret = []
      for r in o:
        ret.append(r)
      return ret
    if isinstance(o, Manager):
      ret = []
      for i in o.all():
        ret.append(i)
      return ret
    if isinstance(o, datetime.datetime):
      return o.isoformat()
    if isinstance(o, datetime.date):
      return o.isoformat()
    return super(ModelEncoder, self).default(o)

class ObjectView(TemplateView):
  def get_context_data(self, request, instance, instances, **kwargs):
    context = super(ObjectView, self).get_context_data(**kwargs)
    context.update(kwargs)
    context['instance'] = instance
    context['instances'] = instances
    return context

  def instance(self, *args, **kwargs):
    return self.model.objects.get(pk=kwargs['id'])

  def instances(self, *args, **kwargs):
    return self.model.objects.all()

  def get(self, request, *args, **kwargs):
    if kwargs['instances']:
      return kwargs['instances']
    return kwargs['instance']

  def post(self, request, *args, **kwargs):
    return True

  def dispatch(self, request, *args, **kwargs):
    format = kwargs.pop('format', None)
    isIndex = kwargs.pop('_index', False)
    instances = None
    instance = None
    if isIndex:
      instances = self.instances(**kwargs)
      template = self.index_template_name
      data = instances
    else:
      instance = self.instance(**kwargs)
      template = self.template_name
      data = instance
    kwargs['instance'] = instance
    kwargs['instances'] = instances
    if request.method == 'GET':
      data = self.get(request, *args, **kwargs)
    if request.method == 'POST':
      data = self.post(request, *args, **kwargs)
    if format:
      if format == 'json':
        data = json.dumps(data, cls=ModelEncoder, indent=True)
        resp = HttpResponse(data)
        resp['Content-Type'] = 'text/plain'
        return resp
      raise NotImplementedError, format
    cxt = self.get_context_data(request, **kwargs)
    return render_to_response(template,
        cxt,
        context_instance=RequestContext(request))
  
  def options(request, *args, **kwargs):
    return ['get', 'post', 'options']

  @classmethod
  def as_url(cls, prefix='', name='view', indexName='index', **kwargs):
    idxArgs = copy(kwargs)
    idxArgs['_index'] = True
    urls = (
        url("^%s(?P<id>[0-9]+)(?:.(?P<format>.*))?$"%(prefix),
          csrf_exempt(cls.as_view()), kwargs, name=name),
        url("^%s(?:.(?P<format>.*))?$"%(prefix),
          cls.as_view(), idxArgs, name=indexName),
    )
    return urls
