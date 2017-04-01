# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-12-21 17:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lunch', '0018_removed_explicit_store'),
    ]

    operations = [
        migrations.RenameField(
            model_name='food',
            old_name='deleted',
            new_name='old_deleted',
        ),
        migrations.AddField(
            model_name='ingredient',
            name='deleted',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='ingredientgroup',
            name='deleted',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name='menu',
            name='deleted',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='ingredientrelation',
            name='food',
            field=models.ForeignKey(help_text='Etenswaar.', on_delete=django.db.models.deletion.CASCADE, related_name='ingredientrelations', to='lunch.Food', verbose_name='etenswaar'),
        ),
        migrations.AlterField(
            model_name='ingredientrelation',
            name='ingredient',
            field=models.ForeignKey(help_text='Ingrediënt.', on_delete=django.db.models.deletion.CASCADE, related_name='ingredientrelations', to='lunch.Ingredient', verbose_name='ingrediënt'),
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'verbose_name': 'ingrediënt', 'verbose_name_plural': 'ingrediënten'},
        ),
        migrations.AddField(
            model_name='quantity',
            name='deleted',
            field=models.DateTimeField(editable=False, null=True),
        ),
    ]