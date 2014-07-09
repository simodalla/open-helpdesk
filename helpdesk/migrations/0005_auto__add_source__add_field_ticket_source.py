# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Source'
        db.create_table('helpdesk_source', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('helpdesk', ['Source'])

        # Adding field 'Ticket.source'
        db.add_column('helpdesk_ticket', 'source',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['helpdesk.Source'], blank=True, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Source'
        db.delete_table('helpdesk_source')

        # Deleting field 'Ticket.source'
        db.delete_column('helpdesk_ticket', 'source_id')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True', 'symmetrical': 'False'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission', 'ordering': "('content_type__app_label', 'content_type__model', 'codename')"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True', 'related_name': "'user_set'", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True', 'related_name': "'user_set'", 'symmetrical': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'", 'object_name': 'ContentType', 'ordering': "('name',)"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'helpdesk.activity': {
            'Meta': {'object_name': 'Activity', 'ordering': "('-created',)"},
            'co_maker': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'blank': 'True', 'related_name': "'co_maker_of_activities'", 'symmetrical': 'False', 'null': 'True'}),
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'related_name': "'maker_of_activities'"}),
            'report': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['helpdesk.Report']", 'blank': 'True', 'null': 'True', 'unique': 'True'}),
            'scheduled_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['helpdesk.Ticket']", 'blank': 'True', 'related_name': "'activities'", 'null': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'helpdesk.attachment': {
            'Meta': {'object_name': 'Attachment', 'ordering': "('-created',)"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '500'}),
            'f': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'helpdesk.category': {
            'Meta': {'object_name': 'Category', 'ordering': "('title',)"},
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'unique': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'helpdesk.message': {
            'Meta': {'object_name': 'Message', 'ordering': "('created',)"},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'blank': 'True', 'related_name': "'recipent_of_messages'", 'null': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'related_name': "'sender_of_messages'"}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['helpdesk.Ticket']", 'blank': 'True', 'related_name': "'messages'", 'null': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'helpdesk.report': {
            'Meta': {'object_name': 'Report', '_ormbases': ['helpdesk.Message'], 'ordering': "('created',)"},
            'action_on_ticket': ('django.db.models.fields.IntegerField', [], {'blank': 'True', 'null': 'True'}),
            'message_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['helpdesk.Message']", 'primary_key': 'True', 'unique': 'True'}),
            'visible_from_requester': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'helpdesk.source': {
            'Meta': {'object_name': 'Source', 'ordering': "('-created',)"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'helpdesk.statuschangeslog': {
            'Meta': {'object_name': 'StatusChangesLog', 'ordering': "('ticket', 'created')"},
            'after': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'before': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'changer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['helpdesk.Ticket']", 'related_name': "'status_changelogs'"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'helpdesk.ticket': {
            'Meta': {'object_name': 'Ticket', 'ordering': "('-created',)"},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'blank': 'True', 'related_name': "'assigned_tickets'", 'null': 'True'}),
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'related_tickets': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['helpdesk.Ticket']", 'blank': 'True', 'related_name': "'related_tickets_rel_+'"}),
            'requester': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'related_name': "'requested_tickets'"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['helpdesk.Source']", 'blank': 'True', 'null': 'True'}),
            'status': ('model_utils.fields.StatusField', [], {'no_check_for_status': 'True', 'max_length': '100', 'default': "'new'"}),
            'status_changed': ('model_utils.fields.MonitorField', [], {'monitor': "'status'", 'default': 'datetime.datetime.now'}),
            'tipologies': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['helpdesk.Tipology']", 'symmetrical': 'False'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'helpdesk.tipology': {
            'Meta': {'unique_together': "(('title', 'category'),)", 'object_name': 'Tipology', 'ordering': "('category__title', 'title')"},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['helpdesk.Category']", 'related_name': "'tipologies'"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sites.Site']", 'blank': 'True', 'related_name': "'tipologies'", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'sites.site': {
            'Meta': {'object_name': 'Site', 'db_table': "'django_site'", 'ordering': "('domain',)"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['helpdesk']