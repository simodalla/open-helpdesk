# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-26 12:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('openhelpdesk', '0002_organizationsetting'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationsetting',
            name='email_background_color',
            field=models.CharField(default='lightskyblue', max_length=20),
        ),
    ]
