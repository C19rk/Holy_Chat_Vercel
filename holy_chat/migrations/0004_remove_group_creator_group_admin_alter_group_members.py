# Generated by Django 5.0.4 on 2024-10-06 10:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('holy_chat', '0003_group_creator_alter_group_members'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='creator',
        ),
        migrations.AddField(
            model_name='group',
            name='admin',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admin_groups', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(related_name='group_members', to=settings.AUTH_USER_MODEL),
        ),
    ]
