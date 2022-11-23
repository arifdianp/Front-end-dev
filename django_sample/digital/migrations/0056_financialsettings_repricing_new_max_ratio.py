# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-04 07:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0055_financialsettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='financialsettings',
            name='repricing_new_max_ratio',
            field=models.FloatField(default=0.5, verbose_name='Ratio to set new maximum betwwn cost+and max'),
        ),
    ]
