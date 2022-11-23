# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-03-27 10:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0095_auto_20180327_0605'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpartcolumns',
            name='cost_saving_pex',
            field=models.BooleanField(default=False, verbose_name='Cost saving 5 Pex'),
        ),
        migrations.AddField(
            model_name='userpartcolumns',
            name='cost_saving_shortage',
            field=models.BooleanField(default=False, verbose_name='Cost saving Shortage'),
        ),
    ]