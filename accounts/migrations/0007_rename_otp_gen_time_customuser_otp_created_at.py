# Generated by Django 5.0.4 on 2024-10-16 18:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_customuser_email'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='otp_gen_time',
            new_name='otp_created_at',
        ),
    ]