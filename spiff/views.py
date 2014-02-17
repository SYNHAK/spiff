from django.views.generic import TemplateView
from copy import copy
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpResponse
from django.db.models import Model, Manager
from django.db.models.query import QuerySet
from django.db.models.fields import FieldDoesNotExist
import datetime

class ModelEncoder(json.JSONEncoder):
  def __init__(self, *args, **kwargs):
    super(ModelEncoder, self).__init__(*args, **kwargs)
    self._seen = []

  def default(self, o):
    if isinstance(o, Model):
      if o in self._seen:
        return "#%s#%s"%(o._meta.object_name.lower(), o.pk)
      self._seen.append(o)
      data = {}
      if hasattr(o, 'serialize'):
        data = o.serialize()
      for f in o._meta.get_all_field_names():
        try:
          data[f] = getattr(o, f)
          if len(o._meta.get_field(f)._choices):
            choices = {}
            for c in o._meta.get_field(f)._choices:
              choices[c[0]] = c[1]
            data["_%s_choices"%(f)] = choices
        except AttributeError:
          pass
        except FieldDoesNotExist:
          pass
      data['_type'] = o._meta.object_name.lower()
      if hasattr(o._meta, 'plural_name'):
        data['_plural_type'] = o._meta.plural_name
      else:
        data['_plural_type'] = o._meta.object_name.lower()+"s"
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
  slug_field = 'id'

  def get_context_data(self, request, instance, instances, **kwargs):
    context = super(ObjectView, self).get_context_data(**kwargs)
    context.update(kwargs)
    context['instance'] = instance
    context['instances'] = instances
    return context

  def instance(self, *args, **kwargs):
    fields = {self.slug_field: kwargs[self.slug_field]}
    return self.model.objects.get(**fields)

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

    if format:
      if format not in ['json']:
        kwargs[self.slug_field] = "%s.%s"%(kwargs[self.slug_field], format)
        return self.dispatch(request, *args, **kwargs)

    if isIndex:
      instances = self.instances(request, **kwargs)
      template = self.index_template_name
      data = instances
    else:
      instance = self.instance(request, **kwargs)
      template = self.template_name
      data = instance
    kwargs['instance'] = instance
    kwargs['instances'] = instances
    if request.method == 'GET':
      data = self.get(request, *args, **kwargs)
    if request.method == 'POST':
      data = self.post(request, *args, **kwargs)
    cxt = self.get_context_data(request, **kwargs)

    if format:
      if format == 'json':
        data = json.dumps(data, cls=ModelEncoder, indent=True)
        resp = HttpResponse(data)
        resp['Content-Type'] = 'text/json'
        return resp
      else:
        raise NotImplemented, "Unsupported format: %s"%(format)
    else:
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
        url("^%s(?:\.(?P<format>.*))?$"%(prefix),
          cls.as_view(), idxArgs, name=indexName),
        url("^%s(?P<%s>[\w\.]+?)(?:\.(?P<format>.*))?$"%(prefix, cls.slug_field),
          csrf_exempt(cls.as_view()), kwargs, name=name),
    )
    return urls
