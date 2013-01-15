# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Action'
        db.create_table('sensors_action', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sensor', self.gf('django.db.models.fields.related.ForeignKey')(related_name='actions', to=orm['sensors.Sensor'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
            ('value', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('sensors', ['Action'])


    def backwards(self, orm):
        # Deleting model 'Action'
        db.delete_table('sensors_action')


    models = {
        'sensors.action': {
            'Meta': {'object_name': 'Action'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sensor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actions'", 'to': "orm['sensors.Sensor']"}),
            'type': ('django.db.models.fields.IntegerField', [], {}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'sensors.sensor': {
            'Meta': {'object_name': 'Sensor'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.IntegerField', [], {})
        },
        'sensors.sensorvalue': {
            'Meta': {'ordering': "['-stamp']", 'object_name': 'SensorValue'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sensor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'values'", 'to': "orm['sensors.Sensor']"}),
            'stamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['sensors']