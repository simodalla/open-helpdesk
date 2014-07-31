# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Source'
        db.create_table('openhelpdesk_source', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('awesome_icon', self.gf('django.db.models.fields.CharField')(blank=True, max_length=100)),
        ))
        db.send_create_signal('openhelpdesk', ['Source'])

        # Adding M2M table for field sites on 'Source'
        m2m_table_name = db.shorten_name('openhelpdesk_source_sites')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('source', models.ForeignKey(orm['openhelpdesk.source'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique(m2m_table_name, ['source_id', 'site_id'])

        # Adding model 'PendingRange'
        db.create_table('openhelpdesk_pendingrange', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('end', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('estimated_end', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('openhelpdesk', ['PendingRange'])

        # Adding model 'Activity'
        db.create_table('openhelpdesk_activity', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('content', self.gf('mezzanine.core.fields.RichTextField')()),
            ('maker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], related_name='maker_of_activities')),
            ('ticket', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, to=orm['openhelpdesk.Ticket'], related_name='activities', null=True)),
            ('report', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['openhelpdesk.Report'], unique=True, null=True, blank=True)),
            ('scheduled_at', self.gf('django.db.models.fields.DateTimeField')(blank=True, null=True)),
        ))
        db.send_create_signal('openhelpdesk', ['Activity'])

        # Adding M2M table for field co_maker on 'Activity'
        m2m_table_name = db.shorten_name('openhelpdesk_activity_co_maker')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('activity', models.ForeignKey(orm['openhelpdesk.activity'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['activity_id', 'user_id'])

        # Adding model 'Attachment'
        db.create_table('openhelpdesk_attachment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('f', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(blank=True, max_length=500)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('openhelpdesk', ['Attachment'])

        # Adding model 'Report'
        db.create_table('openhelpdesk_report', (
            ('message_ptr', self.gf('django.db.models.fields.related.OneToOneField')(primary_key=True, unique=True, to=orm['openhelpdesk.Message'])),
            ('action_on_ticket', self.gf('django.db.models.fields.CharField')(default='no_action', max_length=50)),
            ('visible_from_requester', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('openhelpdesk', ['Report'])

        # Adding model 'StatusChangesLog'
        db.create_table('openhelpdesk_statuschangeslog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('ticket', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openhelpdesk.Ticket'], related_name='status_changelogs')),
            ('before', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('after', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('changer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('openhelpdesk', ['StatusChangesLog'])

        # Adding model 'Tipology'
        db.create_table('openhelpdesk_tipology', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['openhelpdesk.Category'], related_name='tipologies')),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('openhelpdesk', ['Tipology'])

        # Adding M2M table for field sites on 'Tipology'
        m2m_table_name = db.shorten_name('openhelpdesk_tipology_sites')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tipology', models.ForeignKey(orm['openhelpdesk.tipology'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique(m2m_table_name, ['tipology_id', 'site_id'])

        # Adding unique constraint on 'Tipology', fields ['title', 'category']
        db.create_unique('openhelpdesk_tipology', ['title', 'category_id'])

        # Adding model 'Ticket'
        db.create_table('openhelpdesk_ticket', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('content', self.gf('mezzanine.core.fields.RichTextField')()),
            ('status', self.gf('model_utils.fields.StatusField')(default='new', no_check_for_status=True, max_length=100)),
            ('status_changed', self.gf('model_utils.fields.MonitorField')(default=datetime.datetime.now, monitor='status')),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('insert_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], related_name='inserted_tickets')),
            ('requester', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], related_name='requested_tickets')),
            ('assignee', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, to=orm['auth.User'], related_name='assigned_tickets', null=True)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, to=orm['openhelpdesk.Source'], null=True)),
        ))
        db.send_create_signal('openhelpdesk', ['Ticket'])

        # Adding M2M table for field tipologies on 'Ticket'
        m2m_table_name = db.shorten_name('openhelpdesk_ticket_tipologies')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('ticket', models.ForeignKey(orm['openhelpdesk.ticket'], null=False)),
            ('tipology', models.ForeignKey(orm['openhelpdesk.tipology'], null=False))
        ))
        db.create_unique(m2m_table_name, ['ticket_id', 'tipology_id'])

        # Adding M2M table for field related_tickets on 'Ticket'
        m2m_table_name = db.shorten_name('openhelpdesk_ticket_related_tickets')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_ticket', models.ForeignKey(orm['openhelpdesk.ticket'], null=False)),
            ('to_ticket', models.ForeignKey(orm['openhelpdesk.ticket'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_ticket_id', 'to_ticket_id'])

        # Adding model 'Message'
        db.create_table('openhelpdesk_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], related_name='sender_of_messages')),
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, to=orm['auth.User'], related_name='recipent_of_messages', null=True)),
            ('ticket', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, to=orm['openhelpdesk.Ticket'], related_name='messages', null=True)),
        ))
        db.send_create_signal('openhelpdesk', ['Message'])

        # Adding model 'Category'
        db.create_table('openhelpdesk_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=500)),
        ))
        db.send_create_signal('openhelpdesk', ['Category'])


    def backwards(self, orm):
        # Removing unique constraint on 'Tipology', fields ['title', 'category']
        db.delete_unique('openhelpdesk_tipology', ['title', 'category_id'])

        # Deleting model 'Source'
        db.delete_table('openhelpdesk_source')

        # Removing M2M table for field sites on 'Source'
        db.delete_table(db.shorten_name('openhelpdesk_source_sites'))

        # Deleting model 'PendingRange'
        db.delete_table('openhelpdesk_pendingrange')

        # Deleting model 'Activity'
        db.delete_table('openhelpdesk_activity')

        # Removing M2M table for field co_maker on 'Activity'
        db.delete_table(db.shorten_name('openhelpdesk_activity_co_maker'))

        # Deleting model 'Attachment'
        db.delete_table('openhelpdesk_attachment')

        # Deleting model 'Report'
        db.delete_table('openhelpdesk_report')

        # Deleting model 'StatusChangesLog'
        db.delete_table('openhelpdesk_statuschangeslog')

        # Deleting model 'Tipology'
        db.delete_table('openhelpdesk_tipology')

        # Removing M2M table for field sites on 'Tipology'
        db.delete_table(db.shorten_name('openhelpdesk_tipology_sites'))

        # Deleting model 'Ticket'
        db.delete_table('openhelpdesk_ticket')

        # Removing M2M table for field tipologies on 'Ticket'
        db.delete_table(db.shorten_name('openhelpdesk_ticket_tipologies'))

        # Removing M2M table for field related_tickets on 'Ticket'
        db.delete_table(db.shorten_name('openhelpdesk_ticket_related_tickets'))

        # Deleting model 'Message'
        db.delete_table('openhelpdesk_message')

        # Deleting model 'Category'
        db.delete_table('openhelpdesk_category')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'symmetrical': 'False', 'to': "orm['auth.Permission']"})
        },
        'auth.permission': {
            'Meta': {'object_name': 'Permission', 'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)"},
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'symmetrical': 'False', 'to': "orm['auth.Group']", 'related_name': "'user_set'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'symmetrical': 'False', 'to': "orm['auth.Permission']", 'related_name': "'user_set'"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'object_name': 'ContentType', 'db_table': "'django_content_type'", 'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'openhelpdesk.activity': {
            'Meta': {'object_name': 'Activity', 'ordering': "('-created',)"},
            'co_maker': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']", 'related_name': "'co_maker_of_activities'", 'null': 'True'}),
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'related_name': "'maker_of_activities'"}),
            'report': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['openhelpdesk.Report']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'scheduled_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'null': 'True'}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'to': "orm['openhelpdesk.Ticket']", 'related_name': "'activities'", 'null': 'True'}),
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
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'to': "orm['auth.User']", 'related_name': "'recipent_of_messages'", 'null': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'related_name': "'sender_of_messages'"}),
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'to': "orm['openhelpdesk.Ticket']", 'related_name': "'messages'", 'null': 'True'}),
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
            'Meta': {'object_name': 'Report', '_ormbases': ['openhelpdesk.Message'], 'ordering': "('created',)"},
            'action_on_ticket': ('django.db.models.fields.CharField', [], {'default': "'no_action'", 'max_length': '50'}),
            'message_ptr': ('django.db.models.fields.related.OneToOneField', [], {'primary_key': 'True', 'unique': 'True', 'to': "orm['openhelpdesk.Message']"}),
            'visible_from_requester': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'openhelpdesk.source': {
            'Meta': {'object_name': 'Source', 'ordering': "('title',)"},
            'awesome_icon': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '100'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'symmetrical': 'False', 'to': "orm['sites.Site']", 'related_name': "'helpdesk_sources'"}),
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
            'ticket': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['openhelpdesk.Ticket']", 'related_name': "'status_changelogs'"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'openhelpdesk.ticket': {
            'Meta': {'object_name': 'Ticket', 'ordering': "('-created',)"},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'to': "orm['auth.User']", 'related_name': "'assigned_tickets'", 'null': 'True'}),
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insert_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'related_name': "'inserted_tickets'"}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'related_tickets': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['openhelpdesk.Ticket']", 'related_name': "'related_tickets_rel_+'"}),
            'requester': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'related_name': "'requested_tickets'"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'to': "orm['openhelpdesk.Source']", 'null': 'True'}),
            'status': ('model_utils.fields.StatusField', [], {'default': "'new'", 'no_check_for_status': 'True', 'max_length': '100'}),
            'status_changed': ('model_utils.fields.MonitorField', [], {'default': 'datetime.datetime.now', 'monitor': "'status'"}),
            'tipologies': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['openhelpdesk.Tipology']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        'openhelpdesk.tipology': {
            'Meta': {'object_name': 'Tipology', 'ordering': "('category__title', 'title')", 'unique_together': "(('title', 'category'),)"},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['openhelpdesk.Category']", 'related_name': "'tipologies'"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'symmetrical': 'False', 'to': "orm['sites.Site']", 'related_name': "'helpdesk_tipologies'"}),
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