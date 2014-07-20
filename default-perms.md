anonymous user:
  subscription.read_subscriptionplan
  subscription.read_subscriptionperiod
  donations.read_donationsubscriptionplan
  inventory.read_resource
  inventory.read_metadata
  inventory.read_change
  sensors.read_sensor
  sensors.read_sensorvalue
  events.read_event
  membership.read_public_fieldvalue

authenticated users group:
  subscription.create_own_subscription
  subscription.read_own_subscription
  subscription.update_own_subscription
  subscription.delete_own_subscription
  membership.update_own_fieldvalue
  membership.read_own_membershipperiod
  payment.create_own_payment
  payment.read_own_invoice
  events.update_own_event
  events.delete_own_event
  inventory.create_metadata
  inventory.update_metadata
  inventory.delete_metadata

approved members group:
  events.create_own_event
  inventory.create_resource
