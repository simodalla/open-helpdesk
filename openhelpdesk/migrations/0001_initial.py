# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings
import mezzanine.core.fields
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(null=True, editable=False)),
                ('updated', models.DateTimeField(null=True, editable=False)),
                ('content', mezzanine.core.fields.RichTextField(verbose_name='Content')),
                ('scheduled_at', models.DateTimeField(null=True, verbose_name='Scheduled at', blank=True)),
                ('co_maker', models.ManyToManyField(verbose_name='Co Makers', to=settings.AUTH_USER_MODEL, blank=True, related_name='co_maker_of_activities')),
                ('maker', models.ForeignKey(verbose_name='Maker', to=settings.AUTH_USER_MODEL, related_name='maker_of_activities')),
            ],
            options={
                'verbose_name': 'Activity',
                'get_latest_by': 'created',
                'verbose_name_plural': 'Activities',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(null=True, editable=False)),
                ('updated', models.DateTimeField(null=True, editable=False)),
                ('f', models.FileField(verbose_name='File', upload_to='openhelpdesk/attachments/%Y/%m/%d')),
                ('description', models.CharField(verbose_name='Description', max_length=500, blank=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'Attachment',
                'verbose_name_plural': 'Attachments',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(null=True, editable=False)),
                ('updated', models.DateTimeField(null=True, editable=False)),
                ('title', models.CharField(verbose_name='Title', unique=True, max_length=500)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ('title',),
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
                'verbose_name': 'Message',
                'get_latest_by': 'created',
                'verbose_name_plural': 'Messages',
                'ordering': ('created',),
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
                'verbose_name': 'Pending Range',
                'get_latest_by': 'id',
                'verbose_name_plural': 'Pending Ranges',
                'ordering': ('start', 'end'),
            },
        ),
        migrations.CreateModel(
            name='SiteConfiguration',
            fields=[
                ('site', models.OneToOneField(serialize=False, primary_key=True, verbose_name='Site', to='sites.Site')),
                ('_email_addr_from', models.EmailField(verbose_name='Email from', max_length=254, blank=True)),
                ('_email_addr_to_1', models.EmailField(verbose_name='Email to - 1', max_length=254, blank=True)),
                ('_email_addr_to_2', models.EmailField(verbose_name='Email to - 2', max_length=254, blank=True)),
                ('_email_addr_to_3', models.EmailField(verbose_name='Email to - 3', max_length=254, blank=True)),
            ],
            options={
                'verbose_name': 'Site Configuration',
                'verbose_name_plural': 'Site Configurations',
                'ordering': ('site',),
            },
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(null=True, editable=False)),
                ('updated', models.DateTimeField(null=True, editable=False)),
                ('code', models.CharField(verbose_name='code', unique=True, max_length=30)),
                ('title', models.CharField(verbose_name='Title', unique=True, max_length=30)),
                ('awesome_icon', models.CharField(max_length=100, blank=True)),
                ('sites', models.ManyToManyField(verbose_name='Enable on Sites', to='sites.Site', blank=True, related_name='helpdesk_sources')),
            ],
            options={
                'verbose_name': 'Source',
                'verbose_name_plural': 'Sources',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='StatusChangesLog',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(null=True, editable=False)),
                ('updated', models.DateTimeField(null=True, editable=False)),
                ('before', models.CharField(verbose_name='Before', max_length=100)),
                ('after', models.CharField(verbose_name='After', max_length=100)),
                ('changer', models.ForeignKey(verbose_name='Changer', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Status Changelog',
                'get_latest_by': 'created',
                'verbose_name_plural': 'Status Changelogs',
                'ordering': ('ticket', 'created'),
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(null=True, editable=False)),
                ('updated', models.DateTimeField(null=True, editable=False)),
                ('status', model_utils.fields.StatusField(verbose_name='status', choices=[('new', 'New'), ('open', 'Open'), ('pending', 'Pending'), ('closed', 'Closed')], max_length=100, no_check_for_status=True, default='new')),
                ('status_changed', model_utils.fields.MonitorField(verbose_name='status changed', default=django.utils.timezone.now, monitor='status')),
                ('content', models.TextField(verbose_name='Content')),
                ('priority', models.IntegerField(verbose_name='Priority', choices=[(8, 'Urgent'), (4, 'High'), (2, 'Normal'), (1, 'Low')], default=1)),
                ('assignee', models.ForeignKey(null=True, verbose_name='Assignee', to=settings.AUTH_USER_MODEL, blank=True, related_name='assigned_tickets')),
                ('insert_by', models.ForeignKey(editable=False, verbose_name='Insert by', to=settings.AUTH_USER_MODEL, related_name='inserted_tickets')),
                ('related_tickets', models.ManyToManyField(to='openhelpdesk.Ticket', help_text="You can insert one or more related Tickets. Start to type digits for searching into 'id' or 'content' fields of your other Tickets previously inserted.", related_name='_related_tickets_+', blank=True, verbose_name='Related tickets')),
                ('requester', models.ForeignKey(verbose_name='Requester', help_text="You must insert the Requester of Ticket.  Start to type characters for searching into 'username', 'first name' 'last name' or 'email' fields of Requester users.", to=settings.AUTH_USER_MODEL, related_name='requested_tickets')),
                ('site', models.ForeignKey(editable=False, to='sites.Site')),
                ('source', models.ForeignKey(null=True, verbose_name='Source', blank=True, to='openhelpdesk.Source')),
            ],
            options={
                'verbose_name': 'Ticket',
                'get_latest_by': 'created',
                'verbose_name_plural': 'Tickets',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='Tipology',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(null=True, editable=False)),
                ('updated', models.DateTimeField(null=True, editable=False)),
                ('title', models.CharField(verbose_name='Title', max_length=500)),
                ('priority', models.IntegerField(verbose_name='Priority', choices=[(8, 'Urgent'), (4, 'High'), (2, 'Normal'), (1, 'Low')], default=1)),
                ('category', models.ForeignKey(verbose_name='Categories', to='openhelpdesk.Category', related_name='tipologies')),
                ('sites', models.ManyToManyField(verbose_name='Enable on Sites', to='sites.Site', blank=True, related_name='helpdesk_tipologies')),
            ],
            options={
                'verbose_name': 'Tipology',
                'verbose_name_plural': 'Tipologies',
                'ordering': ('category__title', 'title'),
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('message_ptr', models.OneToOneField(serialize=False, primary_key=True, auto_created=True, parent_link=True, to='openhelpdesk.Message')),
                ('action_on_ticket', models.CharField(help_text='Select any action to perform on the ticket.', choices=[('no_action', 'No action (maintain the current status)'), ('put_on_pending', 'Put on pending'), ('remove_from_pending', 'Remove from pending'), ('close', 'Close')], max_length=50, default='no_action', verbose_name='Action on ticket')),
                ('visible_from_requester', models.BooleanField(help_text='Check to make visible this report to the requester.', default=False, verbose_name='Visible from requester')),
            ],
            options={
                'verbose_name': 'Report',
                'get_latest_by': 'created',
                'verbose_name_plural': 'Reports',
                'ordering': ('created',),
            },
            bases=('openhelpdesk.message',),
        ),
        migrations.AddField(
            model_name='ticket',
            name='tipologies',
            field=models.ManyToManyField(help_text='Puoi selezionare al massimo 3 Tipologie.', to='openhelpdesk.Tipology', verbose_name='Tipologies'),
        ),
        migrations.AddField(
            model_name='statuschangeslog',
            name='ticket',
            field=models.ForeignKey(to='openhelpdesk.Ticket', related_name='status_changelogs'),
        ),
        migrations.AddField(
            model_name='message',
            name='recipient',
            field=models.ForeignKey(null=True, verbose_name='Recipient', to=settings.AUTH_USER_MODEL, blank=True, related_name='recipent_of_messages'),
        ),
        migrations.AddField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(verbose_name='Sender', to=settings.AUTH_USER_MODEL, related_name='sender_of_messages'),
        ),
        migrations.AddField(
            model_name='message',
            name='ticket',
            field=models.ForeignKey(null=True, verbose_name='Ticket', to='openhelpdesk.Ticket', blank=True, related_name='messages'),
        ),
        migrations.AddField(
            model_name='activity',
            name='ticket',
            field=models.ForeignKey(null=True, to='openhelpdesk.Ticket', blank=True, related_name='activities'),
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
