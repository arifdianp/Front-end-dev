# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-02-08 02:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0083_delete_grade'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Environment',
        ),
    ]
