# Generated by Django 5.0.4 on 2024-06-06 15:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_payment_plan'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='plan',
        ),
    ]
