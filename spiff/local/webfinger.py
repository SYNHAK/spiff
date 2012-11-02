from django.core.urlresolvers import reverse
import datetime

def handle(acct, xrd):
  xrd.expires = datetime.datetime.utcnow() + datetime.timedelta(0, 10)
