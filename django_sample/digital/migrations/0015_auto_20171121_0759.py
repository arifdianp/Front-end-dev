# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-21 07:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0014_auto_20171121_0755'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PartFamily',
            new_name='ApplianceFamily',
        ),
    ]