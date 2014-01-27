from django.db.models import signals
from django.utils.translation import ugettext_noop as _
from spiff.notification_loader import notification

def create_notice_types(app, created_models, verbosity, **kwargs):
  notification.NoticeType.create(
    'invoice_ready',
    _('Invoice Ready'),
    _('An invoice has been posted to your account')
  )

  notification.NoticeType.create(
    'card_failed',
    _('Card Charge Unsuccessful'),
    _('An attempt was made to charge your card, but it failed')
  )

  notification.NoticeType.create(
    'payment_received',
    _('Payment Received'),
    _('A payment has been received and posted to your account')
  )

signals.post_syncdb.connect(create_notice_types, sender=notification)
