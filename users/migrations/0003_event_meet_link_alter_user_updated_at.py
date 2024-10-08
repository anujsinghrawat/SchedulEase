# Generated by Django 5.1.1 on 2024-09-05 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_active_user_created_at_user_email_user_password_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='meet_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
