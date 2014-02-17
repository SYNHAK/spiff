from spiff.api import SpiffAuthorization
import spiff.subscription.v1_api as subAPI
import models

class DonationPlanResource(subAPI.SubscriptionPlanResource):
  class Meta:
    queryset = models.DonationSubscriptionPlan.objects.all()
    authorization = SpiffAuthorization()
