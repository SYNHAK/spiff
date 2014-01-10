# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        from django.db import transaction
        prevCommit = transaction.get_autocommit()
        transaction.set_autocommit(True)
        for s in orm['sites.Site'].objects.all():
          orm['local.SpaceConfig'].objects.get_or_create(site=s)
        transaction.set_autocommit(prevCommit)

    def backwards(self, orm):
        pass

    models = {
        'local.spaceconfig': {
            'Meta': {'object_name': 'SpaceConfig'},
            'address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'closedIcon': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastChange': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'logo': ('django.db.models.fields.CharField', [], {'default': "'/logo.png'", 'max_length': '100'}),
            'lon': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'open': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'openIcon': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'openSensor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sensors.Sensor']", 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sites.Site']", 'unique': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'local.spacecontact': {
            'Meta': {'object_name': 'SpaceContact'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'space': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['local.SpaceConfig']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'local.spacefeed': {
            'Meta': {'object_name': 'SpaceFeed'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'space': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['local.SpaceConfig']"}),
            'url': ('django.db.models.fields.TextField', [], {})
        },
        'sensors.sensor': {
            'Meta': {'object_name': 'Sensor'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['sites', 'local']
    symmetrical = True
