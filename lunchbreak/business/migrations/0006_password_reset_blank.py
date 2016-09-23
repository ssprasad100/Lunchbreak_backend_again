# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-23 17:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0005_staff_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='password_reset',
            field=models.CharField(blank=True, default='', max_length=64),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='staff',
            name='password_reset',
            field=models.CharField(blank=True, default='', max_length=64),
            preserve_default=False,
        ),
    ]
