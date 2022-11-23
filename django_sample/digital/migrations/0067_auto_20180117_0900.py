# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-17 09:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0066_auto_20180117_0526'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpartfilters',
            name='appliance_list',
            field=models.TextField(default='', verbose_name='Appliance Type List'),
        ),
        migrations.AddField(
            model_name='userpartfilters',
            name='parttype_list',
            field=models.TextField(default='', verbose_name='Part Type List'),
        ),
    ]