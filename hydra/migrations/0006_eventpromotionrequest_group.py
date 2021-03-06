# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-04-18 20:46
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.deletion
import hydra.fields


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0001_initial'),
        ('hydra', '0005_auto_20161203_0036'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventpromotionrequest',
            name='group',
            field=hydra.fields.CrossDatabaseForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_promotion_requests', to='groups.Group', to_field=b'group_id'),
        ),
    ]
