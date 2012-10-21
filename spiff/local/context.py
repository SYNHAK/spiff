from django.contrib.sites.models import get_current_site

def space_info(request):
  return {'site': get_current_site(request)}
