# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-11-25 00:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0017_removed_reservation'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
