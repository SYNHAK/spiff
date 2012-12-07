from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
import datetime

def handle(request, acct, xrd):
  print acct.host
  site = Site.objects.get(domain=acct.host)
  base = "%s://%s"%(request.META['wsgi.url_scheme'], site.domain)
  if request.META['SERVER_PORT'] != '80':
    base = "%s:%s"%(base, request.META['SERVER_PORT'])
  user = User.objects.get(username=acct.userinfo)
  xrd.expires = datetime.datetime.utcnow() + datetime.timedelta(0, 10)
  xrd.aliases.append("%s%s"%(base, reverse('membership:view',
    kwargs={'username':user.username})))
