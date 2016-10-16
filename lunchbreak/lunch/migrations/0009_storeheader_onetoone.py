# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-16 01:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0008_auto_20161005_2026'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='store',
            name='header',
        ),
        migrations.AddField(
            model_name='storeheader',
            name='store',
            field=models.OneToOneField(default=1, help_text='Winkel.', on_delete=django.db.models.deletion.CASCADE, to='lunch.Store', verbose_name='winkel'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='food',
            name='ingredientgroups',
            field=models.ManyToManyField(blank=True, help_text='Ingrediëntengroep.', to='lunch.IngredientGroup', verbose_name='ingrediëntengroep'),
        ),
    ]
