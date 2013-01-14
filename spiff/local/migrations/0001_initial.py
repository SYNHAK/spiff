# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SpaceConfig'
        db.create_table('local_spaceconfig', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sites.Site'], unique=True)),
            ('logo', self.gf('django.db.models.fields.CharField')(default='/logo.png', max_length=100)),
            ('openIcon', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('closedIcon', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('open', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('lat', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('lon', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('lastChange', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('local', ['SpaceConfig'])

        # Adding model 'SpaceContact'
        db.create_table('local_spacecontact', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('space', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['local.SpaceConfig'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('local', ['SpaceContact'])

        # Adding model 'SpaceFeed'
        db.create_table('local_spacefeed', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('space', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['local.SpaceConfig'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('url', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('local', ['SpaceFeed'])


    def backwards(self, orm):
        # Deleting model 'SpaceConfig'
        db.delete_table('local_spaceconfig')

        # Deleting model 'SpaceContact'
        db.delete_table('local_spacecontact')

        # Deleting model 'SpaceFeed'
        db.delete_table('local_spacefeed')


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
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['local']