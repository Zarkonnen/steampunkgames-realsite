# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-09 09:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('steampunkgames', '0006_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='social',
        ),
        migrations.AddField(
            model_name='profile',
            name='twitter',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
        migrations.AddField(
            model_name='profile',
            name='website',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
    ]