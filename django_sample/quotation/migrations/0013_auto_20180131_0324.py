# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-31 03:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quotation', '0012_delete_technology'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TechnologyYAML',
            new_name='Technology',
        ),
    ]
