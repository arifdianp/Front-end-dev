# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-31 02:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quotation', '0009_auto_20171006_0445'),
    ]

    operations = [
        migrations.CreateModel(
            name='TechnologyYAML',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_name', models.CharField(default='', max_length=200)),
                ('file_name', models.CharField(default='', max_length=200)),
            ],
        ),
    ]
