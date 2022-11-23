# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-04-12 03:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0098_auto_20180409_0647'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysisexport',
            name='catalogue',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='digital.Catalogue'),
        ),
        migrations.AlterField(
            model_name='analysisexport',
            name='bulk_upload',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='digital.BulkPartUpload'),
        ),
    ]
