# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-04 07:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('digital', '0036_remove_characteristics_techno_material'),
    ]

    operations = [
        migrations.AddField(
            model_name='parttype',
            name='characteristics',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='digital.Characteristics'),
        ),
        migrations.AlterField(
            model_name='characteristics',
            name='color',
            field=models.CharField(choices=[('NA', 'n/a'), ('GREEN', 'Green'), ('WHITE', 'White'), ('BLACK', 'Black'), ('GREY', 'Grey'), ('SILVER', 'Silver')], default='NA', max_length=20, null=True),
        ),
    ]
