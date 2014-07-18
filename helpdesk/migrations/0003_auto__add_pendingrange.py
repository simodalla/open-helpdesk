# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PendingRange'
        db.create_table('helpdesk_pendingrange', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('end', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('estimated_end', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('helpdesk', ['PendingRange'])


    def backwards(self, orm):
        # Deleting model 'PendingRange'
        db.delete_table('helpdesk_pendingrange')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['auth.Permission']", 'symmetrical': 'False'})
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
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'helpdesk.activity': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'Activity'},
            'co_maker': ('django.db.models.fields.related.ManyToManyField', [], {'null': 'True', 'to': "orm['auth.User']", 'related_name': "'co_maker_of_activities'", 'symmetrical': 'False', 'blank': 'True'}),
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'related_name': "'maker_of_activities'"}),
            'report': ('django.db.models.fields.related.OneToOneField', [], {'null': 'True', 'unique': 'True', 'to': "orm['helpdesk.Report']", 'blank': 'True'}),
            'scheduled_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['helpdesk.Ticket']", 'related_name': "'activities'", 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'helpdesk.attachment': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'Attachment'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '500'}),
            'f': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'helpdesk.category': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Category'},
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '500'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'helpdesk.message': {
            'Meta': {'ordering': "('created',)", 'object_name': 'Message'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['auth.User']", 'related_name': "'recipent_of_messages'", 'blank': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'related_name': "'sender_of_messages'"}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['helpdesk.Ticket']", 'related_name': "'messages'", 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'helpdesk.pendingrange': {
            'Meta': {'ordering': "('start', 'end')", 'object_name': 'PendingRange'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'estimated_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'start': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'helpdesk.report': {
            'Meta': {'object_name': 'Report', 'ordering': "('created',)", '_ormbases': ['helpdesk.Message']},
            'action_on_ticket': ('django.db.models.fields.CharField', [], {'default': "'no_action'", 'max_length': '50'}),
            'message_ptr': ('django.db.models.fields.related.OneToOneField', [], {'primary_key': 'True', 'unique': 'True', 'to': "orm['helpdesk.Message']"}),
            'visible_from_requester': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'helpdesk.source': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Source'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['sites.Site']", 'related_name': "'helpdesk_sources'", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'helpdesk.statuschangeslog': {
            'Meta': {'ordering': "('ticket', 'created')", 'object_name': 'StatusChangesLog'},
            'after': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'before': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'changer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['helpdesk.Ticket']", 'related_name': "'status_changelogs'"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'helpdesk.ticket': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'Ticket'},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['auth.User']", 'related_name': "'assigned_tickets'", 'blank': 'True'}),
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'related_tickets': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['helpdesk.Ticket']", 'related_name': "'related_tickets_rel_+'"}),
            'requester': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'related_name': "'requested_tickets'"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['helpdesk.Source']", 'blank': 'True'}),
            'status': ('model_utils.fields.StatusField', [], {'no_check_for_status': 'True', 'default': "'new'", 'max_length': '100'}),
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
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['sites.Site']", 'related_name': "'helpdesk_tipologies'", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['helpdesk']