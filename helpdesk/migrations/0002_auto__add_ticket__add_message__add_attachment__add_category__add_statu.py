# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Ticket'
        db.create_table('helpdesk_ticket', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('content', self.gf('mezzanine.core.fields.RichTextField')()),
            ('status', self.gf('model_utils.fields.StatusField')(max_length=100, default='new', no_check_for_status=True)),
            ('status_changed', self.gf('model_utils.fields.MonitorField')(monitor='status', default=datetime.datetime.now)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('requester', self.gf('django.db.models.fields.related.ForeignKey')(related_name='requested_tickets', to=orm['auth.User'])),
            ('assignee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='assigned_tickets', null=True, blank=True, to=orm['auth.User'])),
        ))
        db.send_create_signal('helpdesk', ['Ticket'])

        # Adding M2M table for field tipologies on 'Ticket'
        m2m_table_name = db.shorten_name('helpdesk_ticket_tipologies')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ticket', models.ForeignKey(orm['helpdesk.ticket'], null=False)),
            ('tipology', models.ForeignKey(orm['helpdesk.tipology'], null=False))
        ))
        db.create_unique(m2m_table_name, ['ticket_id', 'tipology_id'])

        # Adding M2M table for field related_tickets on 'Ticket'
        m2m_table_name = db.shorten_name('helpdesk_ticket_related_tickets')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_ticket', models.ForeignKey(orm['helpdesk.ticket'], null=False)),
            ('to_ticket', models.ForeignKey(orm['helpdesk.ticket'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_ticket_id', 'to_ticket_id'])

        # Adding model 'Message'
        db.create_table('helpdesk_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sender_of_messages', to=orm['auth.User'])),
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(related_name='recipent_of_messages', null=True, blank=True, to=orm['auth.User'])),
            ('ticket', self.gf('django.db.models.fields.related.ForeignKey')(related_name='messages', null=True, blank=True, to=orm['helpdesk.Ticket'])),
        ))
        db.send_create_signal('helpdesk', ['Message'])

        # Adding model 'Attachment'
        db.create_table('helpdesk_attachment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('f', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('ticket', self.gf('django.db.models.fields.related.ForeignKey')(null=True, blank=True, to=orm['helpdesk.Ticket'])),
        ))
        db.send_create_signal('helpdesk', ['Attachment'])

        # Adding model 'Category'
        db.create_table('helpdesk_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=500)),
        ))
        db.send_create_signal('helpdesk', ['Category'])

        # Adding model 'StatusChangesLog'
        db.create_table('helpdesk_statuschangeslog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('ticket', self.gf('django.db.models.fields.related.ForeignKey')(related_name='status_changelogs', to=orm['helpdesk.Ticket'])),
            ('before', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('after', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('changer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('helpdesk', ['StatusChangesLog'])

        # Adding model 'Activity'
        db.create_table('helpdesk_activity', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('content', self.gf('mezzanine.core.fields.RichTextField')()),
            ('maker', self.gf('django.db.models.fields.related.ForeignKey')(related_name='maker_of_activities', to=orm['auth.User'])),
            ('ticket', self.gf('django.db.models.fields.related.ForeignKey')(related_name='activities', null=True, blank=True, to=orm['helpdesk.Ticket'])),
            ('report', self.gf('django.db.models.fields.related.OneToOneField')(unique=True, null=True, blank=True, to=orm['helpdesk.Report'])),
            ('scheduled_at', self.gf('django.db.models.fields.DateTimeField')(blank=True, null=True)),
        ))
        db.send_create_signal('helpdesk', ['Activity'])

        # Adding M2M table for field co_maker on 'Activity'
        m2m_table_name = db.shorten_name('helpdesk_activity_co_maker')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('activity', models.ForeignKey(orm['helpdesk.activity'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['activity_id', 'user_id'])

        # Adding model 'Report'
        db.create_table('helpdesk_report', (
            ('message_ptr', self.gf('django.db.models.fields.related.OneToOneField')(unique=True, to=orm['helpdesk.Message'], primary_key=True)),
            ('action_on_ticket', self.gf('django.db.models.fields.IntegerField')(blank=True, null=True)),
            ('visible_from_requester', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('helpdesk', ['Report'])

        # Adding model 'Tipology'
        db.create_table('helpdesk_tipology', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tipologies', to=orm['helpdesk.Category'])),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('helpdesk', ['Tipology'])

        # Adding M2M table for field sites on 'Tipology'
        m2m_table_name = db.shorten_name('helpdesk_tipology_sites')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tipology', models.ForeignKey(orm['helpdesk.tipology'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique(m2m_table_name, ['tipology_id', 'site_id'])

        # Adding unique constraint on 'Tipology', fields ['title', 'category']
        db.create_unique('helpdesk_tipology', ['title', 'category_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Tipology', fields ['title', 'category']
        db.delete_unique('helpdesk_tipology', ['title', 'category_id'])

        # Deleting model 'Ticket'
        db.delete_table('helpdesk_ticket')

        # Removing M2M table for field tipologies on 'Ticket'
        db.delete_table(db.shorten_name('helpdesk_ticket_tipologies'))

        # Removing M2M table for field related_tickets on 'Ticket'
        db.delete_table(db.shorten_name('helpdesk_ticket_related_tickets'))

        # Deleting model 'Message'
        db.delete_table('helpdesk_message')

        # Deleting model 'Attachment'
        db.delete_table('helpdesk_attachment')

        # Deleting model 'Category'
        db.delete_table('helpdesk_category')

        # Deleting model 'StatusChangesLog'
        db.delete_table('helpdesk_statuschangeslog')

        # Deleting model 'Activity'
        db.delete_table('helpdesk_activity')

        # Removing M2M table for field co_maker on 'Activity'
        db.delete_table(db.shorten_name('helpdesk_activity_co_maker'))

        # Deleting model 'Report'
        db.delete_table('helpdesk_report')

        # Deleting model 'Tipology'
        db.delete_table('helpdesk_tipology')

        # Removing M2M table for field sites on 'Tipology'
        db.delete_table(db.shorten_name('helpdesk_tipology_sites'))


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'blank': 'True', 'to': "orm['auth.Permission']"})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'object_name': 'Permission', 'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'user_set'", 'symmetrical': 'False', 'blank': 'True', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'user_set'", 'symmetrical': 'False', 'blank': 'True', 'to': "orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'object_name': 'ContentType', 'db_table': "'django_content_type'", 'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'helpdesk.activity': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'Activity'},
            'co_maker': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'co_maker_of_activities'", 'symmetrical': 'False', 'null': 'True', 'blank': 'True', 'to': "orm['auth.User']"}),
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maker': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'maker_of_activities'", 'to': "orm['auth.User']"}),
            'report': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'null': 'True', 'blank': 'True', 'to': "orm['helpdesk.Report']"}),
            'scheduled_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'activities'", 'null': 'True', 'blank': 'True', 'to': "orm['helpdesk.Ticket']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'helpdesk.attachment': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'Attachment'},
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'f': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'blank': 'True', 'to': "orm['helpdesk.Ticket']"}),
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
            'Meta': {'ordering': "('-created',)", 'object_name': 'Message'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recipent_of_messages'", 'null': 'True', 'blank': 'True', 'to': "orm['auth.User']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sender_of_messages'", 'to': "orm['auth.User']"}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'null': 'True', 'blank': 'True', 'to': "orm['helpdesk.Ticket']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'helpdesk.report': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'Report', '_ormbases': ['helpdesk.Message']},
            'action_on_ticket': ('django.db.models.fields.IntegerField', [], {'blank': 'True', 'null': 'True'}),
            'message_ptr': ('django.db.models.fields.related.OneToOneField', [], {'unique': 'True', 'to': "orm['helpdesk.Message']", 'primary_key': 'True'}),
            'visible_from_requester': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'helpdesk.statuschangeslog': {
            'Meta': {'ordering': "('ticket', 'created')", 'object_name': 'StatusChangesLog'},
            'after': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'before': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'changer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'status_changelogs'", 'to': "orm['helpdesk.Ticket']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'helpdesk.ticket': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'Ticket'},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assigned_tickets'", 'null': 'True', 'blank': 'True', 'to': "orm['auth.User']"}),
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'related_tickets': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_tickets_rel_+'", 'blank': 'True', 'to': "orm['helpdesk.Ticket']"}),
            'requester': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'requested_tickets'", 'to': "orm['auth.User']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'status': ('model_utils.fields.StatusField', [], {'max_length': '100', 'default': "'new'", 'no_check_for_status': 'True'}),
            'status_changed': ('model_utils.fields.MonitorField', [], {'monitor': "'status'", 'default': 'datetime.datetime.now'}),
            'tipologies': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['helpdesk.Tipology']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'helpdesk.tipology': {
            'Meta': {'ordering': "('category__title', 'title')", 'object_name': 'Tipology', 'unique_together': "(('title', 'category'),)"},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tipologies'", 'to': "orm['helpdesk.Category']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'tipologies'", 'symmetrical': 'False', 'blank': 'True', 'to': "orm['sites.Site']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'sites.site': {
            'Meta': {'db_table': "'django_site'", 'ordering': "('domain',)", 'object_name': 'Site'},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['helpdesk']