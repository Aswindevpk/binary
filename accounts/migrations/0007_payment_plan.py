# Generated by Django 5.0.4 on 2024-06-06 15:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_subscriptionplan_benefits_subscriptionplan_desc'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='plan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.subscriptionplan'),
        ),
    ]
