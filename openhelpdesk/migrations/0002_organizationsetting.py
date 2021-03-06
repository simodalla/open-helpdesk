# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-22 13:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openhelpdesk', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(editable=False, null=True)),
                ('updated', models.DateTimeField(editable=False, null=True)),
                ('title', models.CharField(max_length=500, unique=True, verbose_name='Title')),
                ('email_domain', models.CharField(max_length=100, unique=True, verbose_name='Email Domain')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('filter_label', models.CharField(max_length=20, verbose_name='Filter label')),
            ],
            options={
                'verbose_name': 'Organization Setting',
                'ordering': ('title',),
                'verbose_name_plural': 'Organization Settings',
                'get_latest_by': 'created',
            },
        ),
    ]
