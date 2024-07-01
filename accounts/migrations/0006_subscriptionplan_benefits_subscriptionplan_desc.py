# Generated by Django 5.0.4 on 2024-06-06 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionplan',
            name='benefits',
            field=models.JSONField(null=True),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='desc',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
    ]
