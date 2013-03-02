import datetime
import calendar
from django.utils.timezone import utc

def monthRange(today=None):
  if today is None:
    today = datetime.datetime.utcnow().replace(tzinfo=utc)
  lastDayOfMonth = calendar.monthrange(today.year, today.month)[1]
  startOfMonth = datetime.datetime(today.year, today.month, 1, tzinfo=utc)
  endOfMonth = datetime.datetime(today.year, today.month, lastDayOfMonth, tzinfo=utc)
  return (startOfMonth, endOfMonth)
