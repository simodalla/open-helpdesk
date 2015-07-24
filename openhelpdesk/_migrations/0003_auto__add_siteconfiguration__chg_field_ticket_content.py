# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SiteConfiguration'
        db.create_table('openhelpdesk_siteconfiguration', (
            ('site', self.gf('django.db.models.fields.related.OneToOneField')(unique=True, primary_key=True, to=orm['sites.Site'])),
            ('_email_addr_from', self.gf('django.db.models.fields.EmailField')(blank=True, max_length=75)),
            ('_email_addr_to_1', self.gf('django.db.models.fields.EmailField')(blank=True, max_length=75)),
            ('_email_addr_to_2', self.gf('django.db.models.fields.EmailField')(blank=True, max_length=75)),
            ('_email_addr_to_3', self.gf('django.db.models.fields.EmailField')(blank=True, max_length=75)),
        ))
        db.send_create_signal('openhelpdesk', ['SiteConfiguration'])


        # Changing field 'Ticket.content'
        db.alter_column('openhelpdesk_ticket', 'content', self.gf('django.db.models.fields.TextField')())

    def backwards(self, orm):
        # Deleting model 'SiteConfiguration'
        db.delete_table('openhelpdesk_siteconfiguration')


        # Changing field 'Ticket.content'
        db.alter_column('openhelpdesk_ticket', 'content', self.gf('mezzanine.core.fields.RichTextField')())

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['auth.Permission']", 'symmetrical': 'False'})
        },
        'auth.permission': {
            'Meta': {'object_name': 'Permission', 'unique_together': "(('content_type', 'codename'),)", 'ordering': "('content_type__app_label', 'content_type__model', 'codename')"},
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['auth.Group']", 'related_name': "'user_set'", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['auth.Permission']", 'related_name': "'user_set'", 'symmetrical': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'object_name': 'ContentType', 'unique_together': "(('app_label', 'model'),)", 'ordering': "('name',)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'openhelpdesk.activity': {
            'Meta': {'object_name': 'Activity', 'ordering': "('-created',)"},
            'co_maker': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['auth.User']", 'related_name': "'co_maker_of_activities'", 'null': 'True', 'symmetrical': 'False'}),
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maker': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'maker_of_activities'", 'to': "orm['auth.User']"}),
            'report': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'unique': 'True', 'null': 'True', 'to': "orm['openhelpdesk.Report']"}),
            'scheduled_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'activities'", 'null': 'True', 'to': "orm['openhelpdesk.Ticket']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'openhelpdesk.attachment': {
            'Meta': {'object_name': 'Attachment', 'ordering': "('-created',)"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '500'}),
            'f': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'openhelpdesk.category': {
            'Meta': {'object_name': 'Category', 'ordering': "('title',)"},
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '500'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'openhelpdesk.message': {
            'Meta': {'object_name': 'Message', 'ordering': "('created',)"},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'recipent_of_messages'", 'null': 'True', 'to': "orm['auth.User']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sender_of_messages'", 'to': "orm['auth.User']"}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'messages'", 'null': 'True', 'to': "orm['openhelpdesk.Ticket']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'openhelpdesk.pendingrange': {
            'Meta': {'object_name': 'PendingRange', 'ordering': "('start', 'end')"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'estimated_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'openhelpdesk.report': {
            'Meta': {'object_name': 'Report', 'ordering': "('created',)", '_ormbases': ['openhelpdesk.Message']},
            'action_on_ticket': ('django.db.models.fields.CharField', [], {'default': "'no_action'", 'max_length': '50'}),
            'message_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'primary_key': 'True', 'to': "orm['openhelpdesk.Message']"}),
            'visible_from_requester': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'openhelpdesk.siteconfiguration': {
            'Meta': {'object_name': 'SiteConfiguration', 'ordering': "('site',)"},
            '_email_addr_from': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            '_email_addr_to_1': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            '_email_addr_to_2': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            '_email_addr_to_3': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'primary_key': 'True', 'to': "orm['sites.Site']"})
        },
        'openhelpdesk.source': {
            'Meta': {'object_name': 'Source', 'ordering': "('title',)"},
            'awesome_icon': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '100'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['sites.Site']", 'related_name': "'helpdesk_sources'", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'openhelpdesk.statuschangeslog': {
            'Meta': {'object_name': 'StatusChangesLog', 'ordering': "('ticket', 'created')"},
            'after': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'before': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'changer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'status_changelogs'", 'to': "orm['openhelpdesk.Ticket']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'openhelpdesk.ticket': {
            'Meta': {'object_name': 'Ticket', 'ordering': "('-created',)"},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assigned_tickets'", 'null': 'True', 'to': "orm['auth.User']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insert_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'inserted_tickets'", 'to': "orm['auth.User']"}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'related_tickets': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'related_tickets_rel_+'", 'to': "orm['openhelpdesk.Ticket']"}),
            'requester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'requested_tickets'", 'to': "orm['auth.User']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'null': 'True', 'to': "orm['openhelpdesk.Source']"}),
            'status': ('model_utils.fields.StatusField', [], {'default': "'new'", 'max_length': '100', 'no_check_for_status': 'True'}),
            'status_changed': ('model_utils.fields.MonitorField', [], {'default': 'datetime.datetime.now', 'monitor': "'status'"}),
            'tipologies': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['openhelpdesk.Tipology']", 'symmetrical': 'False'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'openhelpdesk.tipology': {
            'Meta': {'object_name': 'Tipology', 'unique_together': "(('title', 'category'),)", 'ordering': "('category__title', 'title')"},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tipologies'", 'to': "orm['openhelpdesk.Category']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['sites.Site']", 'related_name': "'helpdesk_tipologies'", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'sites.site': {
            'Meta': {'object_name': 'Site', 'ordering': "('domain',)", 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['openhelpdesk']