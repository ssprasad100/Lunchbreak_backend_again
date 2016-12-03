# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-12-03 12:12
from __future__ import unicode_literals

import Lunchbreak.fields
import django.core.validators
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0021_group_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='discount',
            field=Lunchbreak.fields.RoundingDecimalField(decimal_places=2, default=0, help_text='Korting gegeven op deze bestelling.', max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='korting'),
        ),
        migrations.AlterField(
            model_name='order',
            name='total',
            field=Lunchbreak.fields.RoundingDecimalField(decimal_places=2, default=0, help_text='Totale prijs inclusief korting.', max_digits=7, verbose_name='totale prijs'),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_confirmed',
            field=Lunchbreak.fields.RoundingDecimalField(blank=True, decimal_places=2, default=None, help_text='Totale prijs na correctie van de winkel indien een afgewogen hoeveelheid licht afwijkt van de bestelde hoeveelheid. Dit is al inclusief het kortingspercentage.', max_digits=7, null=True, verbose_name='totale gecorrigeerde prijs'),
        ),
    ]
