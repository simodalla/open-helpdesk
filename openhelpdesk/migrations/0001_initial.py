# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import model_utils.fields
import django.utils.timezone
from django.conf import settings
import mezzanine.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('contenttypes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(null=True, editable=False)),
                ('updated', models.DateTimeField(null=True, editable=False)),
                ('content', mezzanine.core.fields.RichTextField(verbose_name='Content')),
                ('scheduled_at', models.DateTimeField(blank=True, verbose_name='Scheduled at', null=True)),
                ('co_maker', models.ManyToManyField(related_name='co_maker_of_activities', blank=True, to=settings.AUTH_USER_MODEL, verbose_name='Co Makers', null=True)),
                ('maker', models.ForeignKey(related_name='maker_of_activities', verbose_name='Maker', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Activities',
                'ordering': ('-created',),
                'verbose_name': 'Activity',
                'get_latest_by': 'created',
            },
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(null=True, editable=False)),
                ('updated', models.DateTimeField(null=True, editable=False)),
                ('f', models.FileField(verbose_name='File', upload_to='openhelpdesk/attachments/%Y/%m/%d')),
                ('description', models.CharField(blank=True, max_length=500, verbose_name='Description')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': 'Attachments',
                'ordering': ('-created',),
                'verbose_name': 'Attachment',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(null=True, editable=False)),
                ('updated', models.DateTimeField(null=True, editable=False)),
                ('title', models.CharField(unique=True, max_length=500, verbose_name='Title')),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ('title',),
                'verbose_name': 'Category',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(null=True, editable=False)),
                ('updated', models.DateTimeField(null=True, editable=False)),
                ('content', models.TextField(verbose_name='Content')),
            ],
            options={
                'verbose_name_plural': 'Messages',
                'ordering': ('created',),
                'verbose_name': 'Message',
                'get_latest_by': 'created',
            },
        ),
        migrations.CreateModel(
            name='PendingRange',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('start', models.DateTimeField(null=True, editable=False)),
                ('end', models.DateTimeField(null=True, editable=False)),
                ('estimated_end', models.DateTimeField(null=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': 'Pending Ranges',
                'ordering': ('start', 'end'),
                'verbose_name': 'Pending Range',
                'get_latest_by': 'id',
            },
        ),
        migrations.CreateModel(
            name='SiteConfiguration',
            fields=[
                ('site', models.OneToOneField(verbose_name='Site', primary_key=True, serialize=False, to='sites.Site')),
                ('_email_addr_from', models.EmailField(blank=True, max_length=254, verbose_name='Email from')),
                ('_email_addr_to_1', models.EmailField(blank=True, max_length=254, verbose_name='Email to - 1')),
                ('_email_addr_to_2', models.EmailField(blank=True, max_length=254, verbose_name='Email to - 2')),
                ('_email_addr_to_3', models.EmailField(blank=True, max_length=254, verbose_name='Email to - 3')),
            ],
            options={
                'verbose_name_plural': 'Site Configurations',
                'ordering': ('site',),
                'verbose_name': 'Site Configuration',
            },
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(null=True, editable=False)),
                ('updated', models.DateTimeField(null=True, editable=False)),
                ('code', models.CharField(unique=True, max_length=30, verbose_name='code')),
                ('title', models.CharField(unique=True, max_length=30, verbose_name='Title')),
                ('awesome_icon', models.CharField(blank=True, max_length=100)),
                ('sites', models.ManyToManyField(related_name='helpdesk_sources', blank=True, verbose_name='Enable on Sites', to='sites.Site')),
            ],
            options={
                'verbose_name_plural': 'Sources',
                'ordering': ('title',),
                'verbose_name': 'Source',
            },
        ),
        migrations.CreateModel(
            name='StatusChangesLog',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(null=True, editable=False)),
                ('updated', models.DateTimeField(null=True, editable=False)),
                ('before', models.CharField(max_length=100, verbose_name='Before')),
                ('after', models.CharField(max_length=100, verbose_name='After')),
                ('changer', models.ForeignKey(verbose_name='Changer', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Status Changelogs',
                'ordering': ('ticket', 'created'),
                'verbose_name': 'Status Changelog',
                'get_latest_by': 'created',
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(null=True, editable=False)),
                ('updated', models.DateTimeField(null=True, editable=False)),
                ('status', model_utils.fields.StatusField(no_check_for_status=True, max_length=100, choices=[('new', 'New'), ('open', 'Open'), ('pending', 'Pending'), ('closed', 'Closed')], verbose_name='status', default='new')),
                ('status_changed', model_utils.fields.MonitorField(monitor='status', verbose_name='status changed', default=django.utils.timezone.now)),
                ('content', models.TextField(verbose_name='Content')),
                ('priority', models.IntegerField(choices=[(8, 'Urgent'), (4, 'High'), (2, 'Normal'), (1, 'Low')], verbose_name='Priority', default=1)),
                ('assignee', models.ForeignKey(related_name='assigned_tickets', verbose_name='Assignee', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('insert_by', models.ForeignKey(related_name='inserted_tickets', verbose_name='Insert by', editable=False, to=settings.AUTH_USER_MODEL)),
                ('related_tickets', models.ManyToManyField(related_name='related_tickets_rel_+', help_text="You can insert one or more related Tickets. Start to type digits for searching into 'id' or 'content' fields of your other Tickets previously inserted.", blank=True, verbose_name='Related tickets', to='openhelpdesk.Ticket')),
                ('requester', models.ForeignKey(help_text="You must insert the Requester of Ticket.  Start to type characters for searching into 'username', 'first name' 'last name' or 'email' fields of Requester users.", verbose_name='Requester', related_name='requested_tickets', to=settings.AUTH_USER_MODEL)),
                ('site', models.ForeignKey(editable=False, to='sites.Site')),
                ('source', models.ForeignKey(verbose_name='Source', blank=True, to='openhelpdesk.Source', null=True)),
            ],
            options={
                'verbose_name_plural': 'Tickets',
                'ordering': ('-created',),
                'verbose_name': 'Ticket',
                'get_latest_by': 'created',
            },
        ),
        migrations.CreateModel(
            name='Tipology',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(null=True, editable=False)),
                ('updated', models.DateTimeField(null=True, editable=False)),
                ('title', models.CharField(max_length=500, verbose_name='Title')),
                ('priority', models.IntegerField(choices=[(8, 'Urgent'), (4, 'High'), (2, 'Normal'), (1, 'Low')], verbose_name='Priority', default=1)),
                ('category', models.ForeignKey(related_name='tipologies', verbose_name='Categories', to='openhelpdesk.Category')),
                ('sites', models.ManyToManyField(related_name='helpdesk_tipologies', blank=True, verbose_name='Enable on Sites', to='sites.Site')),
            ],
            options={
                'verbose_name_plural': 'Tipologies',
                'ordering': ('category__title', 'title'),
                'verbose_name': 'Tipology',
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('message_ptr', models.OneToOneField(primary_key=True, to='openhelpdesk.Message', serialize=False, auto_created=True, parent_link=True)),
                ('action_on_ticket', models.CharField(help_text='Select any action to perform on the ticket.', max_length=50, choices=[('no_action', 'No action (maintain the current status)'), ('put_on_pending', 'Put on pending'), ('remove_from_pending', 'Remove from pending'), ('close', 'Close')], verbose_name='Action on ticket', default='no_action')),
                ('visible_from_requester', models.BooleanField(help_text='Check to make visible this report to the requester.', verbose_name='Visible from requester', default=False)),
            ],
            options={
                'verbose_name_plural': 'Reports',
                'ordering': ('created',),
                'verbose_name': 'Report',
                'get_latest_by': 'created',
            },
            bases=('openhelpdesk.message',),
        ),
        migrations.AddField(
            model_name='ticket',
            name='tipologies',
            field=models.ManyToManyField(help_text='Puoi selezionare al massimo 3 Tipologie.', verbose_name='Tipologies', to='openhelpdesk.Tipology'),
        ),
        migrations.AddField(
            model_name='statuschangeslog',
            name='ticket',
            field=models.ForeignKey(related_name='status_changelogs', to='openhelpdesk.Ticket'),
        ),
        migrations.AddField(
            model_name='message',
            name='recipient',
            field=models.ForeignKey(related_name='recipent_of_messages', verbose_name='Recipient', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(related_name='sender_of_messages', verbose_name='Sender', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='message',
            name='ticket',
            field=models.ForeignKey(related_name='messages', verbose_name='Ticket', blank=True, to='openhelpdesk.Ticket', null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='ticket',
            field=models.ForeignKey(related_name='activities', null=True, blank=True, to='openhelpdesk.Ticket'),
        ),
        migrations.AlterUniqueTogether(
            name='tipology',
            unique_together=set([('title', 'category')]),
        ),
        migrations.AddField(
            model_name='activity',
            name='report',
            field=models.OneToOneField(null=True, blank=True, to='openhelpdesk.Report'),
        ),
    ]
