# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-28 02:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jb', '0012_remove_coupletechnomaterial_characteristics'),
        ('digital', '0028_auto_20171124_1127'),
    ]

    operations = [
        migrations.AddField(
            model_name='characteristics',
            name='max_X',
            field=models.IntegerField(blank=True, null=True, verbose_name='Maximum X (for Couple Techno-Mat only)'),
        ),
        migrations.AddField(
            model_name='characteristics',
            name='max_Y',
            field=models.IntegerField(blank=True, null=True, verbose_name='Maximum Y (for Couple Techno-Mat only)'),
        ),
        migrations.AddField(
            model_name='characteristics',
            name='max_Z',
            field=models.IntegerField(blank=True, null=True, verbose_name='Maximum Z (for Couple Techno-Mat only)'),
        ),
        migrations.AddField(
            model_name='characteristics',
            name='techno_material',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='jb.CoupleTechnoMaterial', verbose_name='Couple Techno-Material (Only if this card is not attached to a part already)'),
        ),
    ]