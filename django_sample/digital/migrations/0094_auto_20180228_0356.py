# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-02-28 03:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0093_financialcard_pex_volume'),
    ]

    operations = [
        migrations.RenameField(
            model_name='financialcard',
            old_name='pex_volume',
            new_name='pex_volumes',
        ),
        migrations.RenameField(
            model_name='financialcard',
            old_name='shortage_volume',
            new_name='shortage_volumes',
        ),
    ]
