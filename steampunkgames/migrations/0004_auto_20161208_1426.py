# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-08 14:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('steampunkgames', '0003_auto_20161208_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='image',
            field=models.FileField(blank=True, upload_to='profile_images/'),
        ),
        migrations.AddField(
            model_name='profile',
            name='name',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
    ]
