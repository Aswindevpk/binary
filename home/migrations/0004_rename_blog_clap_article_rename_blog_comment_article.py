# Generated by Django 5.0.4 on 2024-07-19 15:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_article_subtitle'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clap',
            old_name='blog',
            new_name='article',
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='blog',
            new_name='article',
        ),
    ]
