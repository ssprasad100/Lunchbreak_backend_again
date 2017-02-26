# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-02-26 15:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0021_safedelete'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='payment_online_only',
            field=models.BooleanField(default=False, help_text='Enkel online betalingen zijn toegestaan.', verbose_name='enkel online betalen'),
        ),
    ]
