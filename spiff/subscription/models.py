from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import utc
import datetime

class SubscriptionPeriod(models.Model):
    name = models.CharField(max_length=255)
    dayOfMonth = models.IntegerField(default=0)
    monthOfYear = models.IntegerField(default=0)

    def __unicode__(self):
      if self.dayOfMonth > 0:
        if self.monthOfYear > 0:
          return "%s: every %s of %s" % (self.name, self.dayOfMonth, self.dayOfYear)
        else:
          return "%s: every %s of the month" % (self.name, self.dayOfMonth)
      else:
        return "%s: every day" % (self.name)

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=255)
    period = models.ForeignKey(SubscriptionPeriod)

    def periodCost(self):
      from spiff.api.plugins import find_api_classes
      for planCls in find_api_classes('models', SubscriptionPlan):
        try:
          plan = planCls.objects.get(pk=self.pk)
        except planCls.DoesNotExist:
          pass
      return plan.calculatePeriodCost()

    def calculatePeriodCost(self):
      raise NotImplementedError

    def createLineItems(self, subscription):
      return []

    def process(self, subscription, now=None):
      if now is None:
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
      nextRun = subscription.nextRun()
      items = []
      if nextRun is None or nextRun <= now:
        items = self.createLineItems(subscription, nextRun)
      subscription.lastProcessed = now
      return items

    def __unicode__(self):
      return "%s, %s"%(self.name, self.period)

class Subscription(models.Model):
    user = models.ForeignKey(User, related_name='subscriptions')
    active = models.BooleanField(default=True)
    plan = models.ForeignKey(SubscriptionPlan, related_name='subscriptions')
    lastProcessed = models.DateTimeField(default=None, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def nextRun(self):
      period = self.plan.period
      nextRun = self.lastProcessed

      if nextRun is None:
        return None
      if period.monthOfYear > 0:
        nextRun = nextRun.replace(month=period.monthOfYear, year=nextRun.year+1)
      if period.dayOfMonth > 0:
        nextRun = nextRun.replace(day=period.dayOfMonth, month=nextRun.month+1)

      return nextRun

    def __unicode__(self):
      return "%s: %s"%(self.user, self.plan)
