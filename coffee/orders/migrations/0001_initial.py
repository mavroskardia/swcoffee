# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Team'
        db.create_table(u'orders_team', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024)),
        ))
        db.send_create_signal(u'orders', ['Team'])

        # Adding model 'Person'
        db.create_table(u'orders_person', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['orders.Team'])),
        ))
        db.send_create_signal(u'orders', ['Person'])

        # Adding model 'Coffee'
        db.create_table(u'orders_coffee', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('one_pound_price', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('two_pound_price', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('five_pound_price', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal(u'orders', ['Coffee'])

        # Adding model 'Order'
        db.create_table(u'orders_order', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['orders.Team'])),
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, unique=True, blank=True)),
            ('placed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'orders', ['Order'])

        # Adding model 'OrderItem'
        db.create_table(u'orders_orderitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['orders.Order'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['orders.Person'])),
            ('coffee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['orders.Coffee'])),
            ('size', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('quantity', self.gf('django.db.models.fields.IntegerField')()),
            ('personal', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('paid', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=5, decimal_places=2)),
        ))
        db.send_create_signal(u'orders', ['OrderItem'])


    def backwards(self, orm):
        # Deleting model 'Team'
        db.delete_table(u'orders_team')

        # Deleting model 'Person'
        db.delete_table(u'orders_person')

        # Deleting model 'Coffee'
        db.delete_table(u'orders_coffee')

        # Deleting model 'Order'
        db.delete_table(u'orders_order')

        # Deleting model 'OrderItem'
        db.delete_table(u'orders_orderitem')


    models = {
        u'orders.coffee': {
            'Meta': {'object_name': 'Coffee'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'five_pound_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'one_pound_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'two_pound_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'})
        },
        u'orders.order': {
            'Meta': {'object_name': 'Order'},
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'unique': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'placed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['orders.Team']"})
        },
        u'orders.orderitem': {
            'Meta': {'object_name': 'OrderItem'},
            'coffee': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['orders.Coffee']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['orders.Order']"}),
            'paid': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '5', 'decimal_places': '2'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['orders.Person']"}),
            'personal': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {}),
            'size': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'orders.person': {
            'Meta': {'object_name': 'Person'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['orders.Team']"})
        },
        u'orders.team': {
            'Meta': {'object_name': 'Team'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['orders']