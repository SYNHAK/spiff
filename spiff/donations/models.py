from django.db import models
from spiff.payment.models import LineItem
from spiff.subscription.models import SubscriptionPlan

class Donation(LineItem):
  pass

class DonationSubscriptionPlan(SubscriptionPlan):
  value = models.FloatField()

  def createLineItems(self, subscription, nextRun):
    return [Donation(
      name="Donation",
      unitPrice = self.value,
      quantity = 1
    )]

  def calculatePeriodCost(self):
    return self.value
