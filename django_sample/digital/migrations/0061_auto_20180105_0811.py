# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-05 08:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0060_financialsettings_yearly_selling_decrease_ratio'),
    ]

    operations = [
        migrations.AddField(
            model_name='financialcard',
            name='positive_longtail_analysis',
            field=models.BooleanField(default=0, verbose_name='Long Tail Analysis positive'),
        ),
        migrations.AddField(
            model_name='financialcard',
            name='positive_obsolete_analysis',
            field=models.BooleanField(default=0, verbose_name='Obsolete Analysis positive'),
        ),
    ]
