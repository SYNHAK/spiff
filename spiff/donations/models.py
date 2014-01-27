from django.db import models
from spiff.payment.models import LineItem, SubscriptionPlan

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
