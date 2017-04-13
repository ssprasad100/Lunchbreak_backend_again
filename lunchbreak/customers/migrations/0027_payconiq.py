# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-04-13 15:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payconiq', '0001_initial'),
        ('customers', '0026_money_new_renamed'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfirmedOrder',
            fields=[
            ],
            options={
                'verbose_name': 'bevestigde bestelling',
                'proxy': True,
                'verbose_name_plural': 'bevestigde bestellingen',
            },
            bases=('customers.order',),
        ),
        migrations.AddField(
            model_name='order',
            name='transaction',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payconiq.Transaction'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment',
            field=models.OneToOneField(blank=True, help_text='Betaling.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='django_gocardless.Payment', verbose_name='betaling'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.IntegerField(choices=[(0, 'Cash'), (1, 'Online (veilig via GoCardless)'), (2, 'Online (veilig via Payconiq)')], default=0, help_text='Betalingswijze.', verbose_name='betalingswijze'),
        ),
    ]
