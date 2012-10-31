# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Sensor'
        db.create_table('sensors_sensor', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('type', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('sensors', ['Sensor'])

        # Adding model 'SensorValue'
        db.create_table('sensors_sensorvalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sensor', self.gf('django.db.models.fields.related.ForeignKey')(related_name='values', to=orm['sensors.Sensor'])),
            ('value', self.gf('django.db.models.fields.TextField')()),
            ('stamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('sensors', ['SensorValue'])


    def backwards(self, orm):
        # Deleting model 'Sensor'
        db.delete_table('sensors_sensor')

        # Deleting model 'SensorValue'
        db.delete_table('sensors_sensorvalue')


    models = {
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