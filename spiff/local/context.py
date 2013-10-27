from django.contrib.sites.models import get_current_site
from django.conf import settings
import forms
import random

def space_info(request):
  site = get_current_site(request)
  base = "%s://%s"%(request.META['wsgi.url_scheme'], site.domain)
  if request.META['SERVER_PORT'] != '80':
    base = "%s:%s"%(base, request.META['SERVER_PORT'])
  return {
    'site': site,
    'ROOT_URL': base
  }

def search_form(request):
  if "query" in request.GET:
    searchForm = forms.SearchForm(request.GET)
  else:
    searchForm = forms.SearchForm()
  return {'searchForm': searchForm}

def greeting_of_the_day(request):
  return {'greetingOfTheDay': random.choice(settings.GREETINGS)}
