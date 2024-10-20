# Generated by Django 5.1.2 on 2024-10-17 17:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('holy_chat', '0011_chatmessage_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='uploads/'),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='holy_chat.group'),
        ),
    ]