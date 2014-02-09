# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Donation'
        db.create_table(u'donations_donation', (
            (u'lineitem_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['payment.LineItem'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'donations', ['Donation'])

        # Adding model 'DonationSubscriptionPlan'
        db.create_table(u'donations_donationsubscriptionplan', (
            (u'subscriptionplan_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['payment.SubscriptionPlan'], unique=True, primary_key=True)),
            ('value', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'donations', ['DonationSubscriptionPlan'])


    def backwards(self, orm):
        # Deleting model 'Donation'
        db.delete_table(u'donations_donation')

        # Deleting model 'DonationSubscriptionPlan'
        db.delete_table(u'donations_donationsubscriptionplan')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'donations.donation': {
            'Meta': {'object_name': 'Donation', '_ormbases': [u'payment.LineItem']},
            u'lineitem_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['payment.LineItem']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'donations.donationsubscriptionplan': {
            'Meta': {'object_name': 'DonationSubscriptionPlan', '_ormbases': [u'payment.SubscriptionPlan']},
            u'subscriptionplan_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['payment.SubscriptionPlan']", 'unique': 'True', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'payment.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'draft': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'dueDate': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'open': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoices'", 'to': u"orm['auth.User']"})
        },
        u'payment.lineitem': {
            'Meta': {'object_name': 'LineItem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': u"orm['payment.Invoice']"}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'quantity': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            'unitPrice': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        u'payment.subscriptionperiod': {
            'Meta': {'object_name': 'SubscriptionPeriod'},
            'dayOfMonth': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monthOfYear': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'payment.subscriptionplan': {
            'Meta': {'object_name': 'SubscriptionPlan'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'period': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['payment.SubscriptionPeriod']"})
        }
    }

    complete_apps = ['donations']