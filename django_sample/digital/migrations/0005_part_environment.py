# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-12 12:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0004_auto_20171112_1205'),
    ]

    operations = [
        migrations.AddField(
            model_name='part',
            name='environment',
            field=models.ManyToManyField(to='digital.Environment'),
        ),
    ]