# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-05 06:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0057_auto_20180105_0144'),
    ]

    operations = [
        migrations.AddField(
            model_name='financialcard',
            name='former_tco',
            field=models.FloatField(blank=True, null=True, verbose_name='Former Total Cost Overall ($US)'),
        ),
    ]
