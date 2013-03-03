from django.db.models import signals
from django.utils.translation import ugettext_noop as _
from spiff.notification_loader import notification

def create_notice_types(app, created_models, verbosity, **kwargs):
  notification.NoticeType.create(
    'account_created',
    _('Account Created'),
    _('A Spiff account has been created for you')
  )

signals.post_syncdb.connect(create_notice_types, sender=notification)

