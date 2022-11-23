# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-02-08 02:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_customuser_currency'),
        ('digital', '0081_auto_20180206_0219'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplianceFamilyDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('retail_price', models.FloatField(default=0.0, verbose_name='Average Retail Price (US$)')),
                ('appliance_family', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='digital.ApplianceFamily')),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Organisation')),
            ],
        ),
        migrations.AddField(
            model_name='appliancefamily',
            name='organisation_details',
            field=models.ManyToManyField(through='digital.ApplianceFamilyDetails', to='users.Organisation'),
        ),
    ]
