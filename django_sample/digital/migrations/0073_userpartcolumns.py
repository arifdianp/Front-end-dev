# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-22 09:23
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('digital', '0072_auto_20180122_0631'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPartColumns',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock', models.BooleanField(default=False, verbose_name='Stock')),
                ('selling_price', models.BooleanField(default=False, verbose_name='Original Selling Price')),
                ('selling_repriced', models.BooleanField(default=False, verbose_name='Repriced Selling Price')),
                ('selling_volumes', models.BooleanField(default=False, verbose_name='Yearly Selling Volumes')),
                ('former_production_cost', models.BooleanField(default=False, verbose_name='Former Production Cost')),
                ('production_cost', models.BooleanField(default=False, verbose_name='SP3D Production Cost')),
                ('former_moq', models.BooleanField(default=False, verbose_name='Former MOQ')),
                ('former_tco', models.BooleanField(default=False, verbose_name='Former TCO')),
                ('sp3d_selling_price', models.BooleanField(default=False, verbose_name='SP3D Selling Price')),
                ('cost_saving_5y', models.BooleanField(default=False, verbose_name='Cost saving 5 year')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='part_columns', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]