# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-24 13:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0012_auto_20161005_2026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertoken',
            name='user',
            field=models.ForeignKey(help_text='Gebruiker.', on_delete=django.db.models.deletion.CASCADE, related_name='tokens', to=settings.AUTH_USER_MODEL, verbose_name='gebruiker'),
        ),
    ]
