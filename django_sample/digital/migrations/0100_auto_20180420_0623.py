# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-04-20 06:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0099_auto_20180412_0313'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='financialsettings',
            name='sp3d_margin_share',
        ),
        migrations.AddField(
            model_name='financialsettings',
            name='client_margin',
            field=models.FloatField(default=0.4, verbose_name='Client Margin'),
        ),
    ]
