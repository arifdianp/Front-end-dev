# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-23 10:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0074_userpartfilters_sort'),
    ]

    operations = [
        migrations.AlterField(
            model_name='part',
            name='name',
            field=models.CharField(default='', max_length=400),
        ),
    ]