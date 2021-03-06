# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-30 02:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import hydra.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bsd', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventPromotionRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=128)),
                ('message', models.CharField(max_length=1024)),
                ('volunteer_count', models.IntegerField()),
                ('status', models.CharField(choices=[(b'new', b'New'), (b'approved', b'Approved'), (b'sent', b'Sent')], default=b'new', max_length=128)),
                ('submitted', models.DateTimeField(auto_now_add=True, null=True)),
                ('sent', models.DateTimeField(blank=True, null=True)),
                ('event', hydra.fields.CrossDatabaseForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, to='bsd.Event')),
                ('host', hydra.fields.CrossDatabaseForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, related_name='event_promotion_requests', to='bsd.Constituent')),
            ],
        ),
        migrations.CreateModel(
            name='EventPromotionRequestThrough',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_promotion_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hydra.EventPromotionRequest')),
                ('recipient', hydra.fields.CrossDatabaseForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, to='bsd.Constituent')),
            ],
        ),
        migrations.AddField(
            model_name='eventpromotionrequest',
            name='recipients',
            field=models.ManyToManyField(related_name='event_promotions', through='hydra.EventPromotionRequestThrough', to='bsd.Constituent'),
        ),
    ]
