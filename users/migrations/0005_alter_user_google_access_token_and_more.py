# Generated by Django 5.1.1 on 2024-09-07 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_google_access_token_user_google_refresh_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='google_access_token',
            field=models.CharField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='google_refresh_token',
            field=models.CharField(blank=True, default=None, null=True),
        ),
    ]
