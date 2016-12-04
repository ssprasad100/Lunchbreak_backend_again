# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-12-04 01:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0024_group_members_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='group',
        ),
        migrations.AddField(
            model_name='order',
            name='group_order',
            field=models.ForeignKey(blank=True, help_text='Groepsbestelling waartoe bestelling behoort.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='customers.GroupOrder', verbose_name='groepsbestelling'),
        ),
    ]
