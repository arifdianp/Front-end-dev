# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-11 01:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jb', '0002_material'),
        ('digital', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='part',
            name='dimension_unit',
            field=models.CharField(choices=[('mm', 'mm'), ('inch', 'inch')], max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='part',
            name='height',
            field=models.FloatField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='part',
            name='length',
            field=models.FloatField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='part',
            name='material',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='jb.Material'),
        ),
        migrations.AddField(
            model_name='part',
            name='weight',
            field=models.FloatField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='part',
            name='weight_unit',
            field=models.CharField(choices=[('gr', 'gr')], max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='part',
            name='width',
            field=models.FloatField(max_length=10, null=True),
        ),
    ]
