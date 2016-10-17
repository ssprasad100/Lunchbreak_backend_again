# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-24 12:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('business', '0006_password_reset_blank'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='staff',
            options={'verbose_name': 'Personeel', 'verbose_name_plural': 'Personeel'},
        ),
        migrations.AlterField(
            model_name='employee',
            name='password',
            field=models.CharField(help_text='Geëncrypteerd wachtwoord', max_length=255, verbose_name='Wachtwoord'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='password_reset',
            field=models.CharField(blank=True, help_text='Code gebruikt om het wachtwoord te veranderen', max_length=64, verbose_name='Wachtwoord reset'),
        ),
        migrations.AlterField(
            model_name='staff',
            name='email',
            field=models.EmailField(help_text='E-mailadres', max_length=255, unique=True, verbose_name='E-mailadres'),
        ),
        migrations.AlterField(
            model_name='staff',
            name='first_name',
            field=models.CharField(help_text='Voornaam', max_length=255, verbose_name='Voornaam'),
        ),
        migrations.AlterField(
            model_name='staff',
            name='last_name',
            field=models.CharField(help_text='Familienaam', max_length=255, verbose_name='Familienaam'),
        ),
        migrations.AlterField(
            model_name='staff',
            name='merchant',
            field=models.ForeignKey(blank=True, help_text='GoCardless account', null=True, on_delete=django.db.models.deletion.SET_NULL, to='django_gocardless.Merchant'),
        ),
        migrations.AlterField(
            model_name='staff',
            name='password',
            field=models.CharField(help_text='Geëncrypteerd wachtwoord', max_length=255, verbose_name='Wachtwoord'),
        ),
        migrations.AlterField(
            model_name='staff',
            name='password_reset',
            field=models.CharField(blank=True, help_text='Code gebruikt om het wachtwoord te veranderen', max_length=64, verbose_name='Wachtwoord reset'),
        ),
        migrations.AlterField(
            model_name='staff',
            name='store',
            field=models.OneToOneField(blank=True, help_text='Winkel', null=True, on_delete=django.db.models.deletion.CASCADE, to='lunch.Store', verbose_name='Winkel'),
        ),
    ]