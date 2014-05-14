# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Tipology.category'
        db.add_column(u'helpdesk_tipology', 'category',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name=u'tipologies', to=orm['helpdesk.Category']),
                      keep_default=False)

        # Removing M2M table for field category on 'Tipology'
        db.delete_table(db.shorten_name(u'helpdesk_tipology_category'))

        # Removing M2M table for field tipology on 'Issue'
        db.delete_table(db.shorten_name(u'helpdesk_issue_tipology'))

        # Adding M2M table for field tipologies on 'Issue'
        m2m_table_name = db.shorten_name(u'helpdesk_issue_tipologies')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('issue', models.ForeignKey(orm[u'helpdesk.issue'], null=False)),
            ('tipology', models.ForeignKey(orm[u'helpdesk.tipology'], null=False))
        ))
        db.create_unique(m2m_table_name, ['issue_id', 'tipology_id'])


    def backwards(self, orm):
        # Deleting field 'Tipology.category'
        db.delete_column(u'helpdesk_tipology', 'category_id')

        # Adding M2M table for field category on 'Tipology'
        m2m_table_name = db.shorten_name(u'helpdesk_tipology_category')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('tipology', models.ForeignKey(orm[u'helpdesk.tipology'], null=False)),
            ('category', models.ForeignKey(orm[u'helpdesk.category'], null=False))
        ))
        db.create_unique(m2m_table_name, ['tipology_id', 'category_id'])

        # Adding M2M table for field tipology on 'Issue'
        m2m_table_name = db.shorten_name(u'helpdesk_issue_tipology')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('issue', models.ForeignKey(orm[u'helpdesk.issue'], null=False)),
            ('tipology', models.ForeignKey(orm[u'helpdesk.tipology'], null=False))
        ))
        db.create_unique(m2m_table_name, ['issue_id', 'tipology_id'])

        # Removing M2M table for field tipologies on 'Issue'
        db.delete_table(db.shorten_name(u'helpdesk_issue_tipologies'))


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'helpdesk.attachment': {
            'Meta': {'ordering': "(u'-created',)", 'object_name': 'Attachment'},
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'f': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['helpdesk.Issue']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        u'helpdesk.category': {
            'Meta': {'ordering': "(u'title',)", 'object_name': 'Category'},
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        u'helpdesk.issue': {
            'Meta': {'ordering': "(u'-created',)", 'object_name': 'Issue'},
            'content': ('mezzanine.core.fields.RichTextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'related_issues': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'related_issues_rel_+'", 'blank': 'True', 'to': u"orm['helpdesk.Issue']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sites.Site']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'tipologies': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "u'issues'", 'symmetrical': 'False', 'to': u"orm['helpdesk.Tipology']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'issues'", 'to': u"orm['auth.User']"})
        },
        u'helpdesk.tipology': {
            'Meta': {'ordering': "(u'category__title', u'title')", 'object_name': 'Tipology'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'tipologies'", 'to': u"orm['helpdesk.Category']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['sites.Site']", 'symmetrical': 'False', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['helpdesk']