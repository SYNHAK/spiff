import models
from django.contrib import admin

admin.site.register(models.Payment)
admin.site.register(models.Invoice)
admin.site.register(models.LineItem)
admin.site.register(models.LineDiscountItem)
admin.site.register(models.Subscription)
admin.site.register(models.SubscriptionPeriod)
