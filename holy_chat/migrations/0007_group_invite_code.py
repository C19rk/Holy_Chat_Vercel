# Generated by Django 5.0.4 on 2024-10-15 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('holy_chat', '0006_notification_notification_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='invite_code',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True),
        ),
    ]
