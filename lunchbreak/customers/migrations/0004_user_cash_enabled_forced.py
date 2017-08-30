# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-25 10:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0003_push_notifications'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='cash_enabled_forced',
            field=models.BooleanField(default=False, help_text='Of deze persoon altijd cash kan betalen, ookal staat dat uitgeschakeld.', verbose_name='forceer cash betalingen'),
        ),
    ]