# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-08 14:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('steampunkgames', '0002_auto_20161208_1322'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='slug',
            field=models.CharField(default='slug', max_length=1000),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='game',
            name='name',
            field=models.CharField(max_length=1000),
        ),
    ]