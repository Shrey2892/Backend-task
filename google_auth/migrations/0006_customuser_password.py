# Generated by Django 5.1.6 on 2025-03-04 05:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('google_auth', '0005_remove_customuser_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='password',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
