# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-09 22:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0002_auto_20170622_1739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertoken',
            name='service',
            field=models.IntegerField(choices=[(0, 'GCM'), (1, 'APNS'), (2, 'Inactive'), (3, 'FCM'), (4, 'WNS')], default=2, verbose_name='Notification service'),
        ),
    ]
