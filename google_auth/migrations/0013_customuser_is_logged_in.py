# Generated by Django 5.1.6 on 2025-03-06 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('google_auth', '0012_alter_customuser_is_superuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_logged_in',
            field=models.BooleanField(default=False),
        ),
    ]
