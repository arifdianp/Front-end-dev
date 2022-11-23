# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-04 03:23
from __future__ import unicode_literals

from django.db import migrations, models
import sp3d_quotation.storage_backends


class Migration(migrations.Migration):

    dependencies = [
        ('quotation', '0006_auto_20170904_0148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='model3d',
            name='file',
            field=models.FileField(blank=True, storage=sp3d_quotation.storage_backends.PrivateMediaStorage(), upload_to='models_3d/'),
        ),
    ]