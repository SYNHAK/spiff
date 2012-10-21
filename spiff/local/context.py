from django.contrib.sites.models import get_current_site
import forms

def space_info(request):
  return {'site': get_current_site(request)}

def search_form(request):
  if "query" in request.GET:
    searchForm = forms.SearchForm(request.GET)
  else:
    searchForm = forms.SearchForm()
  return {'searchForm': searchForm}
