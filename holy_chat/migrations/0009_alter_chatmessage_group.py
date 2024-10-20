# Generated by Django 5.0.4 on 2024-10-15 15:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('holy_chat', '0008_chatmessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatmessage',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='holy_chat.group'),
        ),
    ]